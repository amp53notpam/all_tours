from os import getcwd
from datetime import datetime, date, timedelta
from flask import (
    Blueprint, flash, render_template, current_app, url_for, jsonify, session, typing as ft
)
from flask.views import View
from werkzeug.exceptions import abort
from sqlalchemy.exc import OperationalError, ProgrammingError
from .. import db
from ..models import Lap, Hotel, Tour, TripImage
from locale import setlocale, LC_ALL
from ..utils import make_header, make_short_template, make_dd_lang

lap_bp = Blueprint('lap_bp', __name__,
                   url_prefix="/laps",
                   static_folder='static',
                   template_folder='templates'
                   )

@lap_bp.context_processor
def add_upload_path():
    return dict(upload_path=current_app.config['UPLOAD_FOLDER'])

def get_stats(laps):
    km_tot = 0
    km_done = 0
    tappe_fatte = 0
    tappe_tot = 0
    for lap in laps:
        if lap.Lap.distance:
            km_tot += lap.Lap.distance
        tappe_tot += 1
        try:
            if lap.Lap.date < date.today() or lap.Lap.done:
                if lap.Lap.distance:
                    km_done += lap.Lap.distance
                tappe_fatte += 1
        except AttributeError:
            pass

    return dict([('total_km', round(km_tot, 2)), ('done_km', round(km_done, 2)), ('left_km', km_tot - km_done), ('num_tappe', tappe_tot), ('tappe_fatte', tappe_fatte), ('tappe_da_fare', tappe_tot - tappe_fatte)])

def get_trip():
    active_trip = db.session.execute(db.select(Tour).where(Tour.is_active == True)).fetchone()
    return active_trip.Tour.id


# class Index(View):
#     def dispatch_request(self):
#         return render_template('index.jinja2')
#


class Laps(View):
    def dispatch_request(self):
        try:
            lang = session['lang']
        except KeyError:
            lang = 'it'
        header = make_header(lang)

        try:
            trip_id = get_trip()
            laps = db.session.execute(db.select(Lap).where(Lap.tour_id == trip_id).order_by(Lap.date)).all()
        except (OperationalError, ProgrammingError):
            flash({{ _('Database assente! Prova più tardi') }}, category="error")
            return render_template('index.jinja2', header=header)

        return render_template("laps.jinja2", laps=laps, stats=get_stats(laps), header=header)


class Hotels(View):
    def dispatch_request(self):
        try:
            lang = session['lang']
        except KeyError:
            lang = 'it'
        header = make_header(lang)

        try:
            trip_id = get_trip()
            hotels = db.session.execute(
                db.select(Hotel).join(Lap, Hotel.lap_id == Lap.id).where(Lap.tour_id == trip_id).order_by(
                    Hotel.check_in)).all()
            hotels_unbound = db.session.execute(db.select(Hotel).where(Hotel.lap_id == None)).all()
        except (OperationalError, ProgrammingError):
            flash({{ _('Database assente! Prova più tardi') }}, category="error")
            return render_template('index.jinja2', header=header)

        return render_template("hotels.jinja2", hotels=hotels, hotels_nb=hotels_unbound, splash_page=True, timedelta=timedelta, header=header)


class SingleLap(View):
    def dispatch_request(self, id):
        try:
            lang = session['lang']
        except KeyError:
            lang = 'it'
        header = make_header(lang)

        lap = db.session.get(Lap, id)
        laps = db.session.execute(db.select(Lap).where(Lap.tour_id == lap.tour_id).order_by(Lap.date)).all()
        prev_lap = db.session.execute(db.select(Lap.id, Lap.start, Lap.destination).where(Lap.destination == lap.start)).fetchone()
        next_lap = db.session.execute(db.select(Lap.id, Lap.start, Lap.destination).where(Lap.start == lap.destination)).fetchone()

        return render_template("lap.jinja2", laps=laps, lap=lap, prev_lap=prev_lap, next_lap=next_lap, stats=None, header=header)


class SingleHotel(View):
    def dispatch_request(self, id):
        try:
            lang = session['lang']
        except KeyError:
            lang = 'it'
        header = make_header(lang)

        hotel = db.session.get(Hotel, id)
        hotels = db.session.execute(
            db.select(Hotel).join(Lap, Hotel.lap_id == Lap.id).where(Lap.tour_id == hotel.lap.tour_id).order_by(
                Hotel.check_in)).all()
        hotels_unbound = db.session.execute(db.select(Hotel).where(Hotel.lap_id == None)).all()

        return render_template("hotel.jinja2", header=header, hotels=hotels, hotels_nb=hotels_unbound, hotel=hotel,
                                   timedelta=timedelta)

class SingleLapJS(View):
    def dispatch_request(self, id):
        this_lap = db.session.get(Lap, id)
        prev_lap = db.session.execute(db.select(Lap.id, Lap.start, Lap.destination).where(Lap.destination == this_lap.start)).fetchone()
        next_lap = db.session.execute(db.select(Lap.id, Lap.start, Lap.destination).where(Lap.start == this_lap.destination)).fetchone()

        short_html = make_short_template("lap.jinja2")
        return  render_template(short_html, lap=this_lap, prev_lap=prev_lap, next_lap=next_lap)


class SingleHotelJS(View):
    def dispatch_request(self, id):
        this_hotel = db.session.get(Hotel, id)

        short_html = make_short_template("hotel.jinja2")
        return render_template(short_html, hotel=this_hotel)


class SingleLapMedia(View):
    def dispatch_request(self, id):
        try:
            lang = session['lang']
        except KeyError:
            lang = 'it'
        header = make_header(lang)

        this_lap = db.session.get(Lap, id)
        prev_lap = db.session.execute(db.select(Lap.id, Lap.start, Lap.destination).where(Lap.destination == this_lap.start)).fetchone()
        next_lap = db.session.execute(db.select(Lap.id, Lap.start, Lap.destination).where(Lap.start == this_lap.destination)).fetchone()
        photos = db.session.execute(db.select(TripImage).where(TripImage.lap_id == id).order_by(TripImage.date)).fetchall()

        return render_template("photos.jinja2", header=header, lap=this_lap, prev_lap=prev_lap, next_lap=next_lap, photos=photos)

class SingleLapMediaJS(View):
    def dispatch_request(selfself, id):
        photos = db.session.execute(db.select(TripImage).where(TripImage.lap_id == id).order_by(TripImage.date)).fetchall()

        data = []
        for photo in photos:
            foto = {"src": photo.TripImage.img_src,
                    "width": photo.TripImage.img_width,
                    "height": photo.TripImage.img_height,
                    "date": photo.TripImage.date,
                    "caption": photo.TripImage.caption,
                    "lat": photo.TripImage.lat,
                    "long": photo.TripImage.long
                    }
            data.append(foto)

        return jsonify(data)



# lap_bp.add_url_rule('/', view_func=Index.as_view('index'))
lap_bp.add_url_rule('/tappe', view_func=Laps.as_view('lap_dashboard'))
lap_bp.add_url_rule('/tappe/<int:id>', view_func=SingleLap.as_view('lap'))
lap_bp.add_url_rule('/tappe/<int:id>/js', view_func=SingleLapJS.as_view('lapJS'))
lap_bp.add_url_rule('/tappe/<int:id>/photos', view_func=SingleLapMedia.as_view('lap_media'))
lap_bp.add_url_rule('/tappe/<int:id>/photos/js', view_func=SingleLapMediaJS.as_view('lap_media_js'))
lap_bp.add_url_rule('/alberghi', view_func=Hotels.as_view('hotel_dashboard'))
lap_bp.add_url_rule('/alberghi/<int:id>', view_func=SingleHotel.as_view('hotel'))
lap_bp.add_url_rule('/alberghi/<int:id>/js', view_func=SingleHotelJS.as_view('hotelJS'))
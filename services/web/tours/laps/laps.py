from os import getcwd
from datetime import datetime, date, timedelta
from flask import (
    Blueprint, flash, render_template, current_app, url_for, jsonify, session
)
from flask.views import View
from werkzeug.exceptions import abort
from sqlalchemy.exc import OperationalError, ProgrammingError
from .. import db
from ..models import Lap, Hotel, Tour
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
        header = make_header(session['lang'])

        try:
            trip_id = get_trip()
            laps = db.session.execute(db.select(Lap).where(Lap.tour_id == trip_id).order_by(Lap.date)).all()
        except (OperationalError, ProgrammingError):
            flash({{ _('Database assente! Prova più tardi') }}, category="error")
            return render_template('index.jinja2', header=header)

        return render_template("laps.jinja2", laps=laps, stats=get_stats(laps), header=header)


class Hotels(View):
    def dispatch_request(self):
        header = make_header(session['lang'])

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
        header = make_header(session['lang'])

        lap = db.session.get(Lap, id)
        laps = db.session.execute(db.select(Lap).where(Lap.tour_id == lap.tour_id).order_by(Lap.date)).all()
        prev_lap = db.session.execute(db.select(Lap.id, Lap.start, Lap.destination).where(Lap.destination == lap.start)).fetchone()
        next_lap = db.session.execute(db.select(Lap.id, Lap.start, Lap.destination).where(Lap.start == lap.destination)).fetchone()

        return render_template("lap.jinja2", laps=laps, lap=lap, prev_lap=prev_lap, next_lap=next_lap, stats=None, header=header)


class SingleHotel(View):
    def dispatch_request(self, id):
        header = make_header(session['lang'])

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
        # data = {}
        # if prev_lap:
        #     data["prev_lap"] = {"id": prev_lap.id,
        #                         "start": prev_lap.start,
        #                         "destination": prev_lap.destination}
        # else:
        #     data["previous_lap"] = None
        #
        # if next_lap:
        #     data["next_lap"] = {"id": next_lap.id,
        #                         "start": next_lap.start,
        #                         "destination": next_lap.destination}
        # else:
        #     data["next_lap"] = None
        #
        # data["this_lap"] = {"id": id,
        #                     "start": this_lap.start,
        #                     "destination": this_lap.destination,
        #                     "date": this_lap.date.strftime("%A %d %b %Y"),
        #                     "distance": this_lap.distance,
        #                     "ascent": this_lap.ascent,
        #                     "descent": this_lap.descent,
        #                     "duration": this_lap.duration.strftime("%H:%M:%S") if this_lap.duration else None,
        #                     "done": this_lap.done,
        #                     "gpx": url_for("download_files", filename="tracks/"+this_lap.gpx) if this_lap.gpx else None,
        #                     "update": url_for("dbms_bp.update_lap", id=this_lap.id),
        #                     "delete": url_for("dbms_bp.delete_lap", id=this_lap.id),
        #                     "hotels": [],
        #                     }
        # for hotel in this_lap.hotels:
        #     hotel = {"id": hotel.id,
        #              "URL": url_for("lap_bp.hotel", id=hotel.id),
        #              "name": hotel.name,
        #              }
        #     data["this_lap"]["hotels"].append(hotel)
        #
        # data["this_lap"]["media"] = round(this_lap.distance * 1000 / (this_lap.duration.hour * 3600 + this_lap.duration.minute * 60 + this_lap.duration.second) * 3.6, 2) if this_lap.duration else None

        # response = jsonify(data)
        return  render_template(short_html, lap=this_lap, prev_lap=prev_lap, next_lap=next_lap)


class SingleHotelJS(View):
    def dispatch_request(self, id):
        # def check_out():
        #     if this_hotel.check_out:
        #         return this_hotel.check_out.strftime("%A %d %b %Y")
        #     elif this_hotel.check_in:
        #         return (this_hotel.check_in + timedelta(days=1)).strftime("%A %d %b %Y")
        #     else:
        #         return None

        this_hotel = db.session.get(Hotel, id)

        short_html = make_short_template("hotel.jinja2")
        # data = {}
        # data["this_hotel"] = {"id": this_hotel.id,
        #                       "name": this_hotel.name,
        #                       "photo": url_for("download_files", filename="images/"+this_hotel.photo) if this_hotel.photo else url_for("static", filename="images/default.webp"),
        #                       "address": this_hotel.address,
        #                       "town": this_hotel.town,
        #                       "reserved": this_hotel.reserved,
        #                       "phone": this_hotel.phone,
        #                       "href_phone": this_hotel.href_phone,
        #                       "email": this_hotel.email,
        #                       "coord": None,
        #                       "check_in": this_hotel.check_in.strftime("%A %d %b %Y") if this_hotel.check_in else None,
        #                       "check_out": check_out(),
        #                       "price": this_hotel.price,
        #                       "tappa": {"URL": url_for("lap_bp.tappa", id=this_hotel.lap.id),
        #                                 "start": this_hotel.lap.start,
        #                                 "destination": this_hotel.lap.destination
        #                                 } if this_hotel.lap_id else None,
        #                       "link": this_hotel.link,
        #                       "update": url_for("dbms_bp.update_hotel", id=this_hotel.id),
        #                       "delete": url_for("dbms_bp.delete_hotel", id=this_hotel.id),
        #                       }
        #
        # if this_hotel.lat and this_hotel.long:
        #     data["this_hotel"]["coord"] = {
        #         "latitude": this_hotel.lat,
        #         "longitude": this_hotel.long
        #     }
        #
        # response = jsonify(data)
        #
        # return response
        return render_template(short_html, hotel=this_hotel)


# lap_bp.add_url_rule('/', view_func=Index.as_view('index'))
lap_bp.add_url_rule('/tappe', view_func=Laps.as_view('lap_dashboard'))
lap_bp.add_url_rule('/tappe/<int:id>', view_func=SingleLap.as_view('lap'))
lap_bp.add_url_rule('/tappe/<int:id>/js', view_func=SingleLapJS.as_view('lapJS'))
lap_bp.add_url_rule('/alberghi', view_func=Hotels.as_view('hotel_dashboard'))
lap_bp.add_url_rule('/alberghi/<int:id>', view_func=SingleHotel.as_view('hotel'))
lap_bp.add_url_rule('/alberghi/<int:id>/js', view_func=SingleHotelJS.as_view('hotelJS'))
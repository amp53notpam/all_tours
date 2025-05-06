from datetime import date, timedelta
from flask import (
    Blueprint, flash, render_template, current_app, url_for, jsonify, session, redirect
)
from flask.views import View
from sqlalchemy.exc import OperationalError, ProgrammingError
from .. import db
from ..models import Lap, Hotel, Tour, Media, User
from ..utils import make_header, make_short_template, get_trip
from flask_babel import _

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
    ascent_tot = 0
    descent_tot = 0
    tappe_tot = 0

    km_done = 0
    tappe_fatte = 0
    for lap in laps:
        if lap.distance:
            km_tot += lap.distance
        if lap.ascent:
            ascent_tot += lap.ascent
        if lap.descent:
            descent_tot += lap.descent
        tappe_tot += 1
        try:
            if lap.done:
                if lap.distance:
                    km_done += lap.distance
                tappe_fatte += 1
        except AttributeError:
            pass

    # return dict([('total_km', round(km_tot, 2)), ('done_km', round(km_done, 2)), ('left_km', km_tot - km_done), ('num_tappe', tappe_tot), ('tappe_fatte', tappe_fatte), ('tappe_da_fare', tappe_tot - tappe_fatte)])
    return dict([('total_km', round(km_tot, 2)), ('done_km', round(km_done, 2)), ('num_tappe', tappe_tot), ('tappe_fatte', tappe_fatte), ('tot_ascent', ascent_tot), ('tot_descent', descent_tot)])


def get_laps_prev_next(lap):
    tour = get_trip()
    laps = tour.laps

    lap_idx = laps.index(lap)

    if lap_idx != 0:
        prev_lap = laps[lap_idx - 1]
    else:
        prev_lap = None

    try:
        next_lap = laps[lap_idx + 1]
    except IndexError:
        next_lap = None

    return laps, prev_lap, next_lap


def is_editable():
    if '_user_id' not in session:
        # no user logged in
        return False

    user = db.session.get(User, session['_user_id'])
    if user.is_admin:
        # the admin should be able to edit "ALL" tours
        return True

    trip = db.session.get(Tour, session['trip'])
    if trip in user.tours:
        return True
    else:
        return False


class Laps(View):
    def dispatch_request(self):
        header = make_header()

        try:
            tour = get_trip()
            laps = tour.laps
        except (OperationalError, ProgrammingError):
            flash(_('Database assente! Prova più tardi'), category="error")
            return render_template('index.jinja2', header=header)

        return render_template("laps.jinja2", laps=laps, stats=get_stats(laps), header=header, is_editable=is_editable())


class Hotels(View):
    def dispatch_request(self):
        header = make_header()

        try:
            trip_id = get_trip().id
            hotels = db.session.execute(
                db.select(Hotel).join(Lap, Hotel.lap_id == Lap.id).where(Lap.tour_id == trip_id).order_by(
                    Hotel.check_in)).all()
            # hotels_unbound = None
            # if '_user_id' in session and int(session['_user_id']) == db.session.execute(db.select(Tour).where(Tour.id == trip_id)).scalar().owner.id:
            #     hotels_unbound = db.session.execute(db.select(Hotel).where(Hotel.lap_id == None).where(Hotel.tour_id == trip_id)).all()
        except (OperationalError, ProgrammingError):
            flash(_('Database assente! Prova più tardi'), category="error")
            return render_template('index.jinja2', header=header)

        return render_template("hotels.jinja2", hotels=hotels, hotels_nb=None, splash_page=True, header=header, is_editable=is_editable())


class SingleLap(View):
    def dispatch_request(self, id=None):
        header = make_header()
        lap = db.session.get(Lap, id)
        laps, prev_lap, next_lap = get_laps_prev_next(lap)

        return render_template("lap.jinja2", laps=laps, lap=lap, prev_lap=prev_lap, next_lap=next_lap, stats=None, header=header, is_editable=is_editable())


class SingleHotel(View):
    def dispatch_request(self, id=None):
        header = make_header()

        hotel = db.session.get(Hotel, id)
        hotels = db.session.execute(
            db.select(Hotel).join(Lap, Hotel.lap_id == Lap.id).where(Lap.tour_id == hotel.lap.tour_id).order_by(
                Hotel.check_in)).all()
        hotels_unbound = db.session.execute(db.select(Hotel).where(Hotel.lap_id == None)).all()

        return render_template("hotel.jinja2", header=header, hotels=hotels, hotels_nb=hotels_unbound, hotel=hotel, is_editable=is_editable())


class SingleLapJS(View):
    def dispatch_request(self, id=None):
        this_lap = db.session.get(Lap, id)
        if this_lap is None:
            return ""

        x, prev_lap, next_lap = get_laps_prev_next(this_lap)
        # prev_lap = db.session.execute(db.select(Lap.id, Lap.start, Lap.destination).where(Lap.destination == this_lap.start)).fetchone()
        # next_lap = db.session.execute(db.select(Lap.id, Lap.start, Lap.destination).where(Lap.start == this_lap.destination)).fetchone()

        short_html = make_short_template("lap.jinja2")
        return render_template(short_html, lap=this_lap, prev_lap=prev_lap, next_lap=next_lap, is_editable=is_editable())


class SingleHotelJS(View):
    def dispatch_request(self, id=None):
        this_hotel = db.session.get(Hotel, id)

        short_html = make_short_template("hotel.jinja2")
        return render_template(short_html, hotel=this_hotel, timedelta=timedelta, is_editable=is_editable())


class SingleLapMedia(View):
    def dispatch_request(self, id=None):
        header = make_header()
        can_edit = is_editable()
        this_lap = db.session.get(Lap, id)
        x, prev_lap, next_lap = get_laps_prev_next(this_lap)
        # prev_lap = db.session.execute(db.select(Lap.id, Lap.start, Lap.destination).where(Lap.destination == this_lap.start)).fetchone()
        # next_lap = db.session.execute(db.select(Lap.id, Lap.start, Lap.destination).where(Lap.start == this_lap.destination)).fetchone()
        photos = db.session.execute(db.select(Media).where(Media.lap_id == id).order_by(Media.date)).fetchall()

        return render_template("photos.jinja2", header=header, lap=this_lap, prev_lap=prev_lap, next_lap=next_lap, photos=photos, is_editable=can_edit)


class SingleLapMediaJS(View):
    def dispatch_request(self, id=None):
        lap = db.session.get(Lap, id)
        medias = lap.photos
        # medias = db.session.execute(db.select(Media).where(Media.lap_id == id).order_by(Media.date)).fetchall()

        data = []
        for media in medias:
            foto = {"src": url_for("download_files", filename="images/" + media.media_src),
                    "width": media.media_width,
                    "height": media.media_height,
                    "type": media.media_type,
                    "date": media.date,
                    "caption": media.caption,
                    "lat": media.lat,
                    "long": media.long,
                    "map": url_for("map_bp.photo_map", lat=media.lat, long=media.long) if media.lat else None
                    }
            data.append(foto)

        return jsonify(data)


lap_bp.add_url_rule('/tappe', view_func=Laps.as_view('lap_dashboard'))
lap_bp.add_url_rule('/tappe/<int:id>', view_func=SingleLap.as_view('lap'))
lap_bp.add_url_rule('/tappe/<int:id>/js', view_func=SingleLapJS.as_view('lapJS'))
lap_bp.add_url_rule('/tappe/<int:id>/photos', view_func=SingleLapMedia.as_view('lap_media'))
lap_bp.add_url_rule('/tappe/<int:id>/photos/js', view_func=SingleLapMediaJS.as_view('lap_media_js'))
lap_bp.add_url_rule('/alberghi', view_func=Hotels.as_view('hotel_dashboard'))
lap_bp.add_url_rule('/alberghi/<int:id>', view_func=SingleHotel.as_view('hotel'))
lap_bp.add_url_rule('/alberghi/<int:id>/js', view_func=SingleHotelJS.as_view('hotelJS'))

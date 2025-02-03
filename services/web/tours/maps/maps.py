from datetime import date, timedelta
from os.path import join
from flask import (
    Blueprint, flash, render_template, current_app, url_for, jsonify, session, typing as ft
)
from flask.views import View
from sqlalchemy.exc import OperationalError, ProgrammingError
from .. import db
from ..models import Lap, Hotel, Tour, Media

map_bp = Blueprint('map_bp', __name__,
                   url_prefix="/maps",
                   static_folder='static',
                   template_folder='templates'
                   )


@map_bp.context_processor
def add_upload_path():
    return dict(upload_path=current_app.config['UPLOAD_FOLDER'])


class HotelMap(View):
    def dispatch_request(self, lat, long):
        hotel = db.session.execute(db.select(Hotel).where(Hotel.lat == lat and Hotel.long == long)).scalar()
        gpx = db.session.get(Lap, hotel.lap_id).gpx

        return render_template("map_hotel.jinja2", lat=lat, long=long, popup=hotel.name, media=None, track=gpx)


class LapMap(View):
    def dispatch_request(self, id):
        lap = db.session.get(Lap, id)

        return render_template("map_lap.jinja2", lap=lap, track=lap.gpx)


class PhotoMap(View):
    def dispatch_request(self, lat, long):
        media = db.session.execute(db.select(Media).where(Media.lat == lat and Media.long == long)).scalar()
        media_url = url_for('download_files', filename='images/' + media.media_src)
        popup = f'<a target="_blank" href={media_url}><img src={media_url} style="width: 100px;"></a>'
        gpx = db.session.get(Lap, media.lap_id).gpx
        foto_on_track = db.session.execute(db.select(Media).where(Media.lap_id == media.lap_id, Media.lat != None)).fetchall()

        return render_template("map_photo.jinja2", lat=lat, long=long, popup=popup, media=foto_on_track, track=gpx)


map_bp.add_url_rule('/lap/<int:id>', view_func=LapMap.as_view('lap_map'))
map_bp.add_url_rule('/albergi/<float:lat>/<float:long>', view_func=HotelMap.as_view('hotel_map'))
map_bp.add_url_rule('/foto/<float:lat>/<float:long>', view_func=PhotoMap.as_view('photo_map'))

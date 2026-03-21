from datetime import date, timedelta
from os.path import join
from gpxpy import parse
from flask import (
    Blueprint, flash, render_template, current_app, url_for, redirect, jsonify, session, typing as ft
)
from flask.views import View
from flask_babel import _
from sqlalchemy.exc import OperationalError, ProgrammingError
from .. import db
from ..models import Lap, Hotel, Tour, Media, Gpx

map_bp = Blueprint('map_bp', __name__,
                   url_prefix="/maps",
                   static_folder='static',
                   template_folder='templates'
                   )


@map_bp.context_processor
def add_upload_path():
    return dict(upload_path=current_app.config['UPLOAD_FOLDER'])


def get_lap_bounds(gpx):
    gpx = join(current_app.config['UPLOAD_FOLDER'], "tracks", gpx)
    with open(gpx) as IN:
        gpx = parse(IN)
    if len(gpx.tracks) > 1:
        raise TrackError(_("Nel file %{gpx}s ci sono più tracce", gpx=gpx))
    for track in gpx.tracks:
        if len(track.segments) > 1:
            raise TrackError(_("Traccia con più segmenti"))
        for segment in track.segments:
            points = segment.points
            return (points[0], points[-1])
    return (None, None)


class TrackError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class HotelMap(View):
    def dispatch_request(self, lat=None, long=None):
        hotel = db.session.execute(db.select(Hotel).where(Hotel.lat == lat and Hotel.long == long)).scalar()
        gpx = db.session.get(Lap, hotel.lap_id).primary_gpx

        return render_template("map_hotel.jinja2", lat=lat, long=long, popup=hotel.name, media=None, track=gpx)


class LapMap(View):
    def dispatch_request(self, id=None):
        lap = db.session.get(Lap, id)
        try:
            start, end = get_lap_bounds(lap.primary_gpx)
        except TrackError as e:
            flash(e.message, category="error")
            return redirect(url_for("lap_bp.lap", id=id))

        return render_template("map_lap.jinja2", start=start, end=end, lap=lap, track=lap.primary_gpx)


class LapMapGpx(View):
    def dispatch_request(self, id=None):
        gpx = db.session.get(Gpx, id)
        lap = db.session.get(Lap, gpx.lap_id)

        return render_template("map_lap_extras.jinja2", lap=lap, track=gpx.gpx)


class PhotoMap(View):
    def dispatch_request(self, lat=None, long=None):
        media = db.session.execute(db.select(Media).where(Media.lat == lat and Media.long == long)).scalar()
        media_url = url_for('download_files', filename='images/' + media.media_src)
        popup = f'<a target="_blank" href={media_url}><img src={media_url} style="width: 100px;"></a>'
        gpx = db.session.get(Lap, media.lap_id).primary_gpx
        foto_on_track = db.session.execute(db.select(Media).where(Media.lap_id == media.lap_id, Media.lat != None)).fetchall()

        return render_template("map_photo.jinja2", lat=lat, long=long, popup=popup, media=foto_on_track, track=gpx)


map_bp.add_url_rule('/lap/<int:id>', view_func=LapMap.as_view('lap_map'))
map_bp.add_url_rule('/lap/gpx/<int:id>', view_func=LapMapGpx.as_view('lap_gpx'))
map_bp.add_url_rule('/hotel/<float:lat>/<float:long>', view_func=HotelMap.as_view('hotel_map'))
map_bp.add_url_rule('/media/<float:lat>/<float:long>', view_func=PhotoMap.as_view('photo_map'))

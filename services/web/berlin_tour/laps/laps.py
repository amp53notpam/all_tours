from datetime import datetime, date, timedelta
from flask import (
    Blueprint, flash, render_template, current_app
)
from flask.views import View
from werkzeug.exceptions import abort
from sqlalchemy.exc import OperationalError, ProgrammingError
from .. import db
from ..models import Lap, Hotel
from locale import setlocale, LC_ALL


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


class Index(View):
    def dispatch_request(self):
        return render_template('index.jinja2')


class Laps(View):
    def dispatch_request(self):
        setlocale(LC_ALL, "it_IT.UTF-8")
        try:
            laps = db.session.execute(db.select(Lap).order_by(Lap.date)).all()
        except (OperationalError, ProgrammingError):
            flash("Database assente! Prova più tardi", category="error")
            return render_template('index.jinja2')

        return render_template("laps.jinja2", laps=laps, stats=get_stats(laps))


class Hotels(View):
    def dispatch_request(self):
        try:
            hotels = db.session.execute(db.select(Hotel).order_by(Hotel.check_in)).all()
        except (OperationalError, ProgrammingError):
            flash("Database assente! Prova più tardi", category="error")
            return render_template('index.jinja2')

        return render_template("hotels.jinja2", hotels=hotels)


class SingleLap(View):
    def dispatch_request(self, id):
        lap = db.session.get(Lap, id)
        return render_template("lap.jinja2", lap=lap)


class SingleHotel(View):
    def dispatch_request(self, id):
        hotel = db.session.get(Hotel, id)
        return render_template("hotel.jinja2", hotel=hotel)


lap_bp.add_url_rule('/', view_func=Index.as_view('index'))
lap_bp.add_url_rule('/tappe', view_func=Laps.as_view('lap_dashboard'))
lap_bp.add_url_rule('/tappe/<int:id>', view_func=SingleLap.as_view('tappa'))
lap_bp.add_url_rule('/alberghi', view_func=Hotels.as_view('hotel_dashboard'))
lap_bp.add_url_rule('/alberghi/<int:id>', view_func=SingleHotel.as_view('albergo'))

from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, send_from_directory, get_flashed_messages
)
from werkzeug.exceptions import abort
from sqlalchemy.exc import OperationalError
from .. import db
from ..models import Lap, Hotel
from locale import setlocale, LC_ALL


lap_bp = Blueprint('lap_bp', __name__,
                    url_prefix="/laps",
                    static_folder='static',
                    template_folder='templates'
                   )


@lap_bp.route('/')
def index():
    return render_template('index.jinja2')


@lap_bp.route('/tappe')
def lap_dashboard():
    setlocale(LC_ALL, "it_IT.UTF-8")
    try:
        laps = db.session.execute(db.select(Lap).order_by(Lap.date)).all()
    except OperationalError:
        flash("Database assente! Prova più tardi", category="error")
        return render_template('index.jinja2')

    return render_template("laps.jinja2", laps=laps)


@lap_bp.route('/alberghi')
def hotel_dashboard():
    try:
        hotels = db.session.execute(db.select(Hotel).order_by(Hotel.check_in)).all()
    except OperationalError:
        flash("Database assente! Prova più tardi", category="error")
        return render_template('index.jinja2')

    return render_template("hotels.jinja2", hotels=hotels)


@lap_bp.route('/tappe/<int:id>')
def tappa(id):
    lap = db.session.get(Lap, id)
    return render_template("lap.jinja2", lap=lap)


@lap_bp.route('/alberghi/<int:id>')
def albergo(id):
    hotel = db.session.get(Hotel, id)
    return render_template("hotel.jinja2", hotel=hotel)

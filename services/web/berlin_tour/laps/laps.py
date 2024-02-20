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
                    url_prefix='/laps',
                    static_folder='static',
                    template_folder='templates'
                   )


@lap_bp.route('/')
def index():
    messages = get_flashed_messages()
    print(messages)
    return render_template('index.jinja2')


@lap_bp.route('/tappe')
def lap_dashboard():
    setlocale(LC_ALL, "it_IT.UTF-8")
    try:
        result = db.session.execute(db.select(Lap, Hotel.name, Hotel.photo).join(Lap.hotels).order_by(Lap.date)).all()
    except OperationalError:
        flash("Database assente! Prova più tardi", category="error")
        return render_template('index.jinja2')

    return render_template("laps.jinja2", results=result)


@lap_bp.route('/alberghi')
def hotel_dashboard():
    try:
        result = db.session.execute(db.select(Hotel, Lap.date, Lap.start, Lap.destination).join(Lap.hotels).order_by(Hotel.check_in)).all()
    except OperationalError:
        flash("Database assente! Prova più tardi", category="error")
        return render_template('index.jinja2')

    return render_template("hotels.jinja2", results=result)


@lap_bp.route('/alberghi/<int:id>')
def albergo(id):
    result = db.session.execute(db.select(Hotel, Lap.date, Lap.start, Lap.destination).join(Lap.hotels). where(Hotel.id == id)).first()
    return render_template("hotel.jinja2", result=result)

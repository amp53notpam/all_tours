from os import remove
from os.path import join
from datetime import date, time, timedelta
from re import compile

from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app, session
from flask.views import View
from flask_login import login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from wtforms.validators import ValidationError
from ..models import Lap, Hotel
from .forms import AddLapForm, UpdLapForm, AddHotelForm, UpdHotelForm
from .. import db


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'webp', 'gpx'}

dbms_bp = Blueprint('dbms_bp', __name__,
                    url_prefix='/dbms',
                    static_folder='static',
                    template_folder='templates'
                    )

date_pattern = compile(r'[-./]')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def to_datetime_date(date_str):
    a = date_pattern.split(date_str)
    # normalize the year to 4 digits
    a[2] = f"20{a[2]}" if len(a[2]) == 2 else a[2]
    # normalize day and month to 2 digits
    a = [f"0{x}" if len(x) == 1 else x for x in a]
    a.reverse()
    return date.fromisoformat(''.join(a))


def to_datetime_time(time_str):
    a = time_str.split(":")
    a = [f"0{x}" if len(x) == 1 else x for x in a]
    return time.fromisoformat(''.join(a))


class AddLap(View):
    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self):
        form = AddLapForm()

        if request.method == 'POST':
            data = to_datetime_date(request.form.get('date'))
            partenza = request.form.get('start')
            arrivo = request.form.get('destination')
            distanza = request.form.get('distance')
            salita = request.form.get('ascent')
            discesa = request.form.get('descent')
            tempo = request.form.get('duration')
            tempo = to_datetime_time(tempo) if tempo else tempo
            if 'gpx' in request.files:
                gpx = None
                file = request.files['gpx']
                if file.filename != '' and allowed_file(file.filename):
                    gpx = secure_filename(file.filename)
                    file.save(join(current_app.config['UPLOAD_FOLDER'], 'tracks', gpx))

            # save to database
            new_lap = Lap(
                date=data,
                start=partenza,
                destination=arrivo
            )
            db.session.add(new_lap)
            if distanza:
                new_lap.distance = distanza
            if salita:
                new_lap.ascent = salita
            if discesa:
                new_lap.descent = discesa
            if tempo:
                new_lap.duration = tempo
            if gpx:
                new_lap.gpx = gpx
            db.session.commit()
            flash(f"Aggiunta tappa {partenza} - {arrivo}.", category="info")
            return redirect(url_for("lap_bp.lap_dashboard"))

        return render_template("add_lap.jinja2", form=form)


class UpdLap(View):
    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, id):
        form = UpdLapForm()

        if request.method == 'POST':
            distanza = request.form.get('distance')
            salita = request.form.get('ascent')
            discesa = request.form.get('descent')
            tempo = request.form.get('duration')
            tempo = to_datetime_time(tempo) if tempo else tempo
            if 'gpx' in request.files:
                gpx = None
                file = request.files['gpx']
                if file.filename != '' and allowed_file(file.filename):
                    gpx = secure_filename(file.filename)
                    file.save(join(current_app.config['UPLOAD_FOLDER'], 'tracks', gpx))

            lap = db.session.get(Lap, id)
            if distanza:
                lap.distance = distanza
            if salita:
                lap.ascent = salita
            if discesa:
                lap.descent = discesa
            if tempo:
                lap.duration = tempo
            if gpx:
                lap.gpx = gpx

            db.session.commit()
            flash(f"Aggiornata tappa {lap.start} - {lap.destination}.", category='info')
            return redirect(url_for("lap_bp.lap_dashboard"))

        lap = db.session.get(Lap, id)
        return render_template("upd_lap.jinja2", form=form, lap=lap)


class DeleteLap(View):
    decorators = [login_required]

    def dispatch_request(self, id):
        lap = db.session.get(Lap, id)
        # delete the relevant track file
        if lap.gpx:
            remove(join(current_app.config['UPLOAD_FOLDER'], 'tracks', lap.gpx))
        db.session.delete(lap)
        db.session.commit()
        flash(f"Cancellata tappa {lap.start} - {lap.destination}", category='info')
        return redirect(url_for("lap_bp.lap_dashboard"))


class AddHotel(View):
    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self):
        form = AddHotelForm()

        if request.method == 'POST':
            name = request.form.get('name')
            address = request.form.get('address')
            town = request.form.get('town')
            check_in = to_datetime_date(request.form.get('check_in'))
            lap_id = db.session.scalars(db.select(Lap.id).where(Lap.date == check_in)).first()
            if lap_id is None:
                flash(f"Nessuna tappa in data {request.form.get('check_in')}", category='error')
                return redirect(url_for("lap_bp.hotel_dashboard"))

            check_out = request.form.get('check_out')
            check_out = to_datetime_date(check_out) if check_out else check_in + timedelta(1)
            price = request.form.get('price')
            website = request.form.get('website')
            reserved = True if request.form.get('reserved') else False
            if 'photo' in request.files:
                photo = None
                file = request.files['photo']
                if file.filename != '' and allowed_file(file.filename):
                    photo = secure_filename(file.filename)
                    file.save(join(current_app.config['UPLOAD_FOLDER'], 'images', photo))

            # save to database
            new_hotel = Hotel(
                name=name,
                address=address,
                town=town,
                check_in=check_in,
                lap_id=lap_id
            )
            db.session.add(new_hotel)
            if check_out:
                new_hotel.check_out = check_out
            if price:
                new_hotel.price = price
            if website:
                new_hotel.link = website
            new_hotel.reserved = reserved
            if photo:
                new_hotel.photo = photo

            db.session.commit()
            flash(f"Aggiunto albergo {name} a {town}.", category="info")
            return redirect(url_for("lap_bp.hotel_dashboard"))

        return render_template("add_hotel.jinja2", form=form)


class UpdHotel(View):
    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, id):
        form = UpdHotelForm()
        if request.method == 'POST':
            check_out = request.form.get('check_out')
            check_out = to_datetime_date(check_out) if check_out else check_out
            price = request.form.get('price')
            website = request.form.get('website')
            reserved = True if request.form.get('reserved') else False
            if 'photo' in request.files:
                photo = None
                file = request.files['photo']
                if file.filename != '' and allowed_file(file.filename):
                    photo = secure_filename(file.filename)
                    file.save(join(current_app.config['UPLOAD_FOLDER'], 'images', photo))

            hotel = db.session.get(Hotel, id)
            if check_out:
                hotel.check_out = check_out
            if price:
                hotel.price = price
            if website:
                hotel.link = website
            hotel.reserved = reserved
            if photo:
                hotel.photo = photo

            db.session.commit()
            flash(f"Hotel {hotel.name} aggiornato.", category="info")
            return redirect(url_for("lap_bp.hotel_dashboard"))

        hotel = db.session.get(Hotel, id)
        return render_template("upd_hotel.jinja2", form=form, hotel=hotel)


class DeleteHotel(View):
    decorators = [login_required]

    def dispatch_request(self, id):
        hotel = db.session.get(Hotel, id)
        # delete the hotel's photo
        if hotel.photo:
            remove(join(current_app.config['UPLOAD_FOLDER'], 'images', hotel.photo))
        db.session.delete(hotel)
        db.session.commit()
        flash(f"Cancellato albergo {hotel.name}", category='info')
        return redirect(url_for("lap_bp.hotel_dashboard"))


dbms_bp.add_url_rule('/lap/add/', view_func=AddLap.as_view("add_lap"))
dbms_bp.add_url_rule('/lap/update/<int:id>', view_func=UpdLap.as_view("update_lap"))
dbms_bp.add_url_rule('/lap/delete/<int:id>', view_func=DeleteLap.as_view('delete_lap'))
dbms_bp.add_url_rule('/hotel/add/', view_func=AddHotel.as_view("add_hotel"))
dbms_bp.add_url_rule('/hotel/update/<int:id>', view_func=UpdHotel.as_view("update_hotel"))
dbms_bp.add_url_rule('/hotel/delete/<int:id>', view_func=DeleteHotel.as_view('delete_hotel'))

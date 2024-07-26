from os import remove
from os.path import join
from datetime import date, time, timedelta
from re import compile
from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from flask.views import View
from flask_login import login_required
from werkzeug.utils import secure_filename
from ..models import Lap, Hotel, Tour
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
    if not date_str:
        return None
    a = date_pattern.split(date_str)
    # normalize the year to 4 digits
    a[2] = f"20{a[2]}" if len(a[2]) == 2 else a[2]
    # normalize day and month to 2 digits
    a = [f"0{x}" if len(x) == 1 else x for x in a]
    a.reverse()
    return date.fromisoformat(''.join(a))


def to_datetime_time(time_str):
    if not time_str:
        return None
    a = time_str.split(":")
    a = [f"0{x}" if len(x) == 1 else x for x in a]
    return time.fromisoformat(''.join(a))


def get_trip():
    active_trip = db.session.execute(db.select(Tour).where(Tour.is_active == True)).fetchone()
    return active_trip.Tour.id


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
            gpx = None
            if 'gpx' in request.files:
                file = request.files['gpx']
                if file.filename != '' and allowed_file(file.filename):
                    gpx = secure_filename(file.filename)
                    file.save(join(current_app.config['UPLOAD_FOLDER'], 'tracks', gpx))
            trip_id = get_trip()
            # save to database
            new_lap = Lap(
                date=data,
                start=partenza,
                destination=arrivo,
                tour_id=trip_id,
            )
            db.session.add(new_lap)
            new_lap.distance = distanza if distanza else 0
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
            current_app.logger.info(f"Aggiunta tappa {partenza} - {arrivo}.")
            return redirect(url_for("lap_bp.lap_dashboard"))

        return render_template("add_lap.jinja2", form=form)


class UpdLap(View):
    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, id):
        form = UpdLapForm()

        if request.method == 'POST':
            data = to_datetime_date(request.form.get('date'))
            distanza = request.form.get('distance')
            salita = request.form.get('ascent')
            discesa = request.form.get('descent')
            tempo = request.form.get('duration')
            tempo = to_datetime_time(tempo) if tempo else tempo
            fatta = True if request.form.get('done') else False
            gpx = None
            if 'gpx' in request.files:
                file = request.files['gpx']
                if file.filename != '' and allowed_file(file.filename):
                    gpx = secure_filename(file.filename)
                    file.save(join(current_app.config['UPLOAD_FOLDER'], 'tracks', gpx))

            lap = db.session.get(Lap, id)
            if data != lap.date:
                lap.date = data
            if distanza:
                lap.distance = distanza
            if salita:
                lap.ascent = salita
            if discesa:
                lap.descent = discesa
            if tempo:
                lap.duration = tempo
            lap.done = fatta
            if gpx:
                lap.gpx = gpx

            db.session.commit()
            flash(f"Tappa {lap.start} - {lap.destination} aggiornata .", category='info')
            current_app.logger.info(f"Aggiornata tappa {lap.start} - {lap.destination}.")
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
        current_app.logger.info(f"Cancellata tappa {lap.start} - {lap.destination}")
        return redirect(url_for("lap_bp.lap_dashboard"))


class AddHotel(View):
    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self):
        form = AddHotelForm()

        if request.method == 'POST':
            lap_id = None
            name = request.form.get('name')
            address = request.form.get('address')
            town = request.form.get('town')
            check_in = to_datetime_date(request.form.get('check_in'))
            check_out = to_datetime_date(request.form.get('check_out'))
            if check_in:
                lap_id = db.session.scalars(db.select(Lap.id).where(Lap.date == check_in)).first()
                if lap_id is None:
                    flash("Albergo non associabile ad alcuna tappa. ", category='warning')

                if check_out and check_out <= check_in:
                    # data di check-out anteriore o uguale a quella di check-in???
                    flash("Date di check-in e check-out incongrenti.", category='error')
                    return redirect(url_for("lap_bp.hotel_dashboard"))

            price = request.form.get('price')
            website = request.form.get('website')
            reserved = True if request.form.get('reserved') else False
            photo = None
            if 'photo' in request.files:
                file = request.files['photo']
                if file.filename != '' and allowed_file(file.filename):
                    photo = secure_filename(file.filename)
                    file.save(join(current_app.config['UPLOAD_FOLDER'], 'images', photo))

            # save to database
            new_hotel = Hotel(
                name=name,
                address=address,
                town=town,
            )
            db.session.add(new_hotel)
            if lap_id:
                new_hotel.lap_id = lap_id
            if check_in:
                new_hotel.check_in = check_in
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
            current_app.logger.info(f"Aggiunto albergo {name} a {town}.")
            return redirect(url_for("lap_bp.hotel_dashboard"))

        return render_template("add_hotel.jinja2", form=form)


class UpdHotel(View):
    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, id):
        form = UpdHotelForm()

        if request.method == 'POST':
            check_in = to_datetime_date(request.form.get('check_in'))
            check_out = to_datetime_date(request.form.get('check_out'))
            if check_in:
                lap_id = db.session.scalars(db.select(Lap.id).where(Lap.date == check_in)).first()
                if lap_id is None:
                    flash("Albergo non associabile ad alcuna tappa. ", category='warning')

                if check_out and check_out <= check_in:
                    # data di check-out anteriore o uguale a quella di check-in???
                    flash("Date di check-in e check-out incongrenti.", category='error')
                    return redirect(url_for("lap_bp.hotel_dashboard"))

            price = request.form.get('price')
            website = request.form.get('website')
            reserved = True if request.form.get('reserved') else False
            photo = None
            if 'photo' in request.files:
                file = request.files['photo']
                if file.filename != '' and allowed_file(file.filename):
                    photo = secure_filename(file.filename)
                    file.save(join(current_app.config['UPLOAD_FOLDER'], 'images', photo))

            hotel = db.session.get(Hotel, id)
            if check_in:
                hotel.check_in = check_in
            if check_out:
                hotel.check_out = check_out
            if lap_id:
                hotel.lap_id = lap_id
            if price:
                hotel.price = price
            if website:
                hotel.link = website
            hotel.reserved = reserved
            if photo:
                hotel.photo = photo

            db.session.commit()
            flash(f"Hotel {hotel.name} aggiornato.", category="info")
            current_app.logger.info(f"Aggiornato hotel {hotel.name}.")
            return redirect(url_for("lap_bp.hotel_dashboard"))

        hotel = db.session.get(Hotel, id)
        return render_template("upd_hotel.jinja2", form=form, hotel=hotel, timedelta=timedelta)


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
        current_app.logger.info(f"Cancellato albergo {hotel.name}.")
        return redirect(url_for("lap_bp.hotel_dashboard"))


dbms_bp.add_url_rule('/lap/add/', view_func=AddLap.as_view("add_lap"))
dbms_bp.add_url_rule('/lap/update/<int:id>', view_func=UpdLap.as_view("update_lap"))
dbms_bp.add_url_rule('/lap/delete/<int:id>', view_func=DeleteLap.as_view('delete_lap'))
dbms_bp.add_url_rule('/hotel/add/', view_func=AddHotel.as_view("add_hotel"))
dbms_bp.add_url_rule('/hotel/update/<int:id>', view_func=UpdHotel.as_view("update_hotel"))
dbms_bp.add_url_rule('/hotel/delete/<int:id>', view_func=DeleteHotel.as_view('delete_hotel'))
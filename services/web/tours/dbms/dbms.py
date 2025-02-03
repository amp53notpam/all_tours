from os import remove
from os.path import join
from datetime import datetime, date, time, timedelta
from re import compile
from subprocess import Popen, PIPE, STDOUT
from shlex import split
from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app, session, jsonify
from flask.views import View
from flask_login import login_required
from flask_babel import _
from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from ..models import Lap, Hotel, Tour, Media, Users
from .forms import AddTourForm, AddLapForm, UpdLapForm, AddHotelForm, UpdHotelForm, LoadMediaForm, TourMgmtForm
from .. import db
from ..utils import make_header, translations

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'webp', 'gpx', 'mp4'}

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
    active_trip = db.session.execute(db.select(Tour).where(Tour.is_active)).scalar()
    return active_trip.id


def update_all_dates(laps, new_date, old_date):
    delta_t = new_date - old_date
    if delta_t.days < 0:
        if db.session.execute(db.select(Lap).where(Lap.date.between(new_date, old_date - timedelta(days=1))).order_by(Lap.date)).all():
            raise DateOverlappingError(_("Non ci sono abbastanza giorni liberi per spostare la tappa indietro nel tempo"))
        hotel = db.session.execute(db.select(Hotel).where(Hotel.check_out.between(new_date + timedelta(days=1), old_date)).order_by(Hotel.check_out)).all()
        if hotel:
            raise DateOverlappingError(_(f'La data di check out dell\'albergo "{hotel[0].Hotel.name}" è incompatibile con la nuova data'))
    for lap in laps:
        lap.date += delta_t
        for hotel in lap.hotels:
            hotel.check_in += delta_t
            hotel.check_out += delta_t


def add_geo_tag(media, track):
    p = Popen(split(f"exiftool -s2 -n -gpslatitude -gpslongitude {media}"), stdout=PIPE, stderr=STDOUT, encoding="utf-8")
    position, error = p.communicate()
    if not position:
        Popen(split(f"exiftool -geotag {track} -geosync=1:00:00 {media}"), stdout=PIPE, stderr=STDOUT, encoding="utf-8").wait()
        Popen(split(f"exiftool -delete_original! {media}"), stdout=PIPE, stderr=STDOUT).wait()


def register_media(id, gpx, media, caption):
    track = join(current_app.config['UPLOAD_FOLDER'], 'tracks', gpx)
    media_dir = join(current_app.config['UPLOAD_FOLDER'], 'images')
    media_fp = join(media_dir, media)

    add_geo_tag(media_fp, track)
    p = Popen(split(f"exiftool -s2 -d '%Y%m%dT%H%M%S' -datetimeoriginal -createdate -mimetype {media_fp}"), stdout=PIPE, stderr=STDOUT, encoding="utf-8")
    meta, error = p.communicate()
    meta = {x[0]: x[1] for x in [y.split(': ') for y in meta.splitlines()]}
    if 'CreateDate' in meta:
        media_date = datetime.fromisoformat(meta['CreateDate'])
    elif 'DateTimeOriginal' in meta:
        media_date = datetime.fromisoformat(meta['DateTimeOriginal'])
    else:
        media_date = None

    media_type, x = meta['MIMEType'].split('/')

    if media_type == 'image':
        p = Popen(split(f"exiftool -s2 -n -imageheight -imagewidth {media_fp}"), stdout=PIPE, stderr=STDOUT, encoding="utf-8")
        meta, error = p.communicate()
        meta = {x[0]: float(x[1]) for x in [y.split(': ') for y in meta.splitlines()]}

        media_height = meta['ImageHeight'] if 'ImageHeight' in meta else 0
        media_width = meta['ImageWidth'] if 'ImageWidth' in meta else 0

        Popen(split(f"convert {media_fp} -resize {(lambda x: 1024 / max(x) * 100)([media_height, media_width])}% {media_fp}")).wait()

    p = Popen(split(f"exiftool -s2 -n -imageheight -imagewidth -orientation -rotation -gpslatitude -gpslongitude {media_fp}"), stdout=PIPE, stderr=STDOUT, encoding="utf-8")
    meta, error = p.communicate()
    meta = {x[0]: x[1] for x in [y.split(': ') for y in meta.splitlines()]}

    # orientation = meta['Orientation'] if 'Orientation' in meta else 0
    latitude = float(meta['GPSLatitude']) if 'GPSLatitude' in meta else None
    longitude = float(meta['GPSLongitude']) if 'GPSLongitude' in meta else None
    if 'Orientation' in meta:
        orientation = int(meta['Orientation'])
    elif 'Rotation' in meta:
        orientation = (int(meta['Rotation']) // 90) % 2 * 5
    media_width = int(meta['ImageWidth']) if orientation <= 4 else int(meta['ImageHeight'])
    media_height = int(meta['ImageHeight']) if orientation <= 4 else int(meta['ImageWidth'])

    db_media = db.session.execute(db.select(Media).where(Media.media_src == media)).fetchone()
    if db_media is None or db_media.Media.lap_id != id:
        new_picture = Media(
            lap_id=id,
            media_src=media,
            media_width=media_width,
            media_height=media_height,
            media_type=media_type,
            lat=latitude,
            long=longitude,
            caption=caption
        )
        if media_date:
            new_picture.date = media_date
        db.session.add(new_picture)
    else:
        db_media.Media.media_width = media_width
        db_media.Media.media_height = media_height
        db_media.Media.media = media_date
        db_media.Media.lat = latitude
        db_media.Media.long = longitude
        if caption:
            db_media.Media.caption = caption

    try:
        db.session.commit()
    except IntegrityError:
        current_app.logger.warning(f"Tentativo di caricare la foto {media} già caricata per la stessa tappa.")


def check_lap_date(date):
    tour = db.session.execute(db.select(Tour).where(Tour.is_active)).scalar()
    laps = db.session.execute(db.select(Lap).where(Lap.tour_id == tour.id).order_by(Lap.date)).scalars()
    for lap in laps:
        hotels = db.session.execute(db.select(Hotel).where(Hotel.tour_id == tour.id).order_by(Hotel.check_in)).scalars()
        for hotel in hotels:
            ckin = hotel.check_in
            ckout = hotel.check_out
            if ckin < lap.date < ckout:
                raise DateOverlappingError(_(f"La data della tappa e il soggiorno all'albergo {hotel.name} si sovrappongono"))


def check_hotel_date(check_in, check_out):
    if (check_out - check_in).days == 1:
        return
    laps = db.session.execute(db.select(Lap).where(Lap.date.between(check_in + timedelta(days=1), check_out - timedelta(days=1)))).scalars()
    laps = " / ".join([f"{lap.start}-{lap.destination}" for lap in laps])
    if laps:
        raise DateOverlappingError(_(f'La durata del soggiorno si sovrappone alle tappe "{laps}"'))


class DateOverlappingError(Exception):
    def __init__(self, msg):
        self.msg = msg


class AddLap(View):
    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self):
        form = AddLapForm()
        header = make_header()

        if request.method == 'POST':
            data = date.fromisoformat(request.form.get('date'))
            partenza = request.form.get('start')
            arrivo = request.form.get('destination')
            distanza = request.form.get('distance')
            salita = request.form.get('ascent')
            discesa = request.form.get('descent')
            tempo = request.form.get('duration')
            tempo = time.fromisoformat(tempo) if tempo else tempo
            gpx = None
            if 'gpx' in request.files:
                file = request.files['gpx']
                if file.filename != '':
                    if allowed_file(file.filename):
                        gpx = secure_filename(file.filename)
                        file.save(join(current_app.config['UPLOAD_FOLDER'], 'tracks', gpx))
                    else:
                        flash(_('Il file "%(file)s" non è una traccia gpx ed è stato ignorato', file=file.filename),
                              category="warning")

            trip_id = get_trip()
            try:
                check_lap_date(data)
            except DateOverlappingError as e:
                flash(e.msg, category="error")
                return render_template("add_lap.jinja2", form=form, header=header)

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
            try:
                db.session.commit()
            except IntegrityError:
                flash(_('In questo viaggio è gia definita una tappa alla stessa data'), category="error")
            else:
                flash(_("Aggiunta tappa %(partenza)s - %(arrivo)s.", partenza=partenza, arrivo=arrivo), category="info")
                current_app.logger.info(f"Aggiunta tappa {partenza} - {arrivo}.")

                lap_id = db.session.execute(db.select(Lap.id).where(Lap.start == partenza).where(Lap.destination == arrivo)).scalar()
                hotels = db.session.execute(db.select(Hotel).where(Hotel.check_in == data)).scalars()
                if hotels:
                    for hotel in hotels:
                        hotel.lap_id = lap_id
                db.session.commit()

            return redirect(url_for("lap_bp.lap_dashboard"))

        return render_template("add_lap.jinja2", form=form, header=header)


class UpdLap(View):
    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, id):
        form = UpdLapForm()
        header = make_header()

        if request.method == 'POST':
            data = request.form.get('date')
            data = date.fromisoformat(data) if data else data
            distanza = request.form.get('distance')
            salita = request.form.get('ascent')
            discesa = request.form.get('descent')
            tempo = request.form.get('duration')
            tempo = time.fromisoformat(tempo) if tempo else tempo
            # tempo = to_datetime_time(tempo) if tempo else tempo
            fatta = True if request.form.get('done') else False
            gpx = None
            if 'gpx' in request.files:
                file = request.files['gpx']
                if file.filename != '':
                    if allowed_file(file.filename):
                        gpx = secure_filename(file.filename)
                        file.save(join(current_app.config['UPLOAD_FOLDER'], 'tracks', gpx))
                    else:
                        flash(_('Il file "%(file)s" non è una traccia gpx ed è stato ignorato', file=file.filename),
                              category="warning")

            lap = db.session.get(Lap, id)
            if data and data != lap.date:
                if (data - lap.date).days > 0:
                    laps = db.session.execute(db.select(Lap).where(Lap.tour_id == lap.tour_id).where(Lap.date >= lap.date).order_by(desc(Lap.date))).scalars()
                else:
                    laps = db.session.execute(db.select(Lap).where(Lap.tour_id == lap.tour_id).where(Lap.date >= lap.date).order_by(Lap.date)).scalars()
                try:
                    update_all_dates(laps, data, lap.date)
                except DateOverlappingError as e:
                    flash(e.msg, category="error")
                    return render_template("upd_lap.jinja2", form=form, lap=lap, header=header)

                # lap.date = data
                # for hotel in lap.hotels:
                #     hotel.check_in += delta_t
                #     hotel.check_out += delta_t
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

            flash(_('Tappa %(start)s - %(destination)s aggiornata.', start=lap.start, destination=lap.destination), category='info')
            current_app.logger.info(f"Aggiornata tappa {lap.start} - {lap.destination}.")
            return redirect(url_for("lap_bp.lap_dashboard"))

        lap = db.session.get(Lap, id)
        return render_template("upd_lap.jinja2", form=form, lap=lap, header=header)


class LoadLapMedia(View):
    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, id):
        form = LoadMediaForm()

        if request.method == 'POST':
            caption = request.form.get("caption")
            media_file = None
            if 'media_file' in request.files:
                file = request.files['media_file']
                if file.filename != '' and allowed_file(file.filename):
                    media_file = secure_filename(file.filename)
                    file.save(join(current_app.config['UPLOAD_FOLDER'], 'images', media_file))

            lap = db.session.get(Lap, id)
            if media_file:
                lap.has_photos = True
            db.session.commit()
            try:
                register_media(lap.id, lap.gpx, media_file, caption)
            except ZeroDivisionError:
                flash(_(f"Il file {media_file} potrebbe essere corrotto"), category='error')

            return redirect(url_for("lap_bp.lap", id=id))

        lap = db.session.get(Lap, id)
        header = make_header()
        return render_template("load_media.jinja2", form=form, lap=lap, header=header)


class DeleteLap(View):
    decorators = [login_required]

    def dispatch_request(self, id):
        lap = db.session.get(Lap, id)
        if lap:
            # delete the relevant track file
            if lap.gpx:
                remove(join(current_app.config['UPLOAD_FOLDER'], 'tracks', lap.gpx))
            db.session.delete(lap)
            db.session.commit()
            flash(_('Cancellata tappa %(start)s - %(destination)s.', start=lap.start, destination=lap.destination), category='info')
            current_app.logger.info(f"Cancellata tappa {lap.start} - {lap.destination}")

        return redirect(url_for("lap_bp.lap_dashboard"))


class DeleteMedia(View):
    decorators = [login_required]

    def dispatch_request(self, media):
        md = db.session.execute(db.select(Media).where(Media.media_src == media)).scalar()
        lap_id = md.lap_id
        try:
            remove(join(current_app.config['UPLOAD_FOLDER'], 'images', media))
        except FileNotFoundError:
            pass
        db.session.delete(md)
        db.session.commit()
        if not db.session.execute(db.select(func.count(Media.id)).where(Media.lap_id == lap_id)).scalar():
            lap = db.session.get(Lap, lap_id)
            lap.has_photos = False
            db.session.commit()

        return jsonify("Done")


class AddHotel(View):
    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self):
        form = AddHotelForm()
        header = make_header()

        if request.method == 'POST':
            lap_id = request.form.get('lap')
            name = request.form.get('name')
            address = request.form.get('address')
            town = request.form.get('town')
            stay = request.form.get('stay')
            phone = request.form.get('phone')
            email = request.form.get('email')
            latitude = request.form.get('geo_lat')
            longitude = request.form.get('geo_long')
            price = request.form.get('price')
            website = request.form.get('website')
            reserved = True if request.form.get('reserved') else False
            photo = None
            if 'photo' in request.files:
                file = request.files['photo']
                if file.filename != '':
                    if allowed_file(file.filename):
                        photo = secure_filename(file.filename)
                        file.save(join(current_app.config['UPLOAD_FOLDER'], 'images', photo))
                    else:
                        flash(_('Il file "%(file)s" non è una immagine ed è stato ignorato', file=file.filename),
                              category="warning")

            lap = db.session.get(Lap, lap_id)
            tour_id = db.session.execute(db.select(Tour).where(Tour.is_active)).scalar().id
            # save to database
            new_hotel = Hotel(
                name=name,
                address=address,
                town=town,
            )

            new_hotel.lap_id = lap_id
            new_hotel.tour_id = tour_id
            new_hotel.check_in = lap.date
            new_hotel.check_out = new_hotel.check_in + timedelta(days=int(stay))

            try:
                check_hotel_date(new_hotel.check_in, new_hotel.check_out)
            except DateOverlappingError as e:
                flash(e.msg, category="error")
                laps = db.session.execute(db.select(Lap).where(
                    Lap.tour_id == db.session.execute(db.select(Tour).where(Tour.is_active)).scalar().id).order_by(
                    Lap.date)).scalars()
                # form.lap.choices = [("", _("Scegli la tappa"), {"disabled": "disabled"})]
                form.lap.choices = ([(lap.id, f"{lap.start} - {lap.destination}", dict()) for lap in laps])
                form.lap.choices.extend([("", "--------", {"disabled": "disabled"})])
                form.lap.default = ""
                form.process([])

                return render_template("add_hotel.jinja2", form=form, header=header)

            if phone:
                new_hotel.phone = phone
                new_hotel.href_phone = ''.join(phone.split())
            if email:
                new_hotel.email = email
            if latitude and longitude:
                new_hotel.lat = latitude
                new_hotel.long = longitude

            if price:
                new_hotel.price = price
            if website:
                new_hotel.link = website
            new_hotel.reserved = reserved
            if photo:
                new_hotel.photo = photo

            db.session.add(new_hotel)
            db.session.commit()
            flash(_('Aggiunto albergo %(name)s a %(town)s.', name=name, town=town), category="info")
            current_app.logger.info(f"Aggiunto albergo {name} a {town}.")
            return redirect(url_for("lap_bp.hotel_dashboard"))

        laps = db.session.execute(db.select(Lap).where(Lap.tour_id == db.session.execute(db.select(Tour).where(Tour.is_active)).scalar().id).order_by(Lap.date)).scalars()
        # form.lap.choices = [("", _("Scegli la tappa"), {"disabled": "disabled"})]
        form.lap.choices = [(lap.id, f"{lap.start} - {lap.destination}", dict()) for lap in laps]
        form.lap.choices.extend([("", "--------", {"disabled": "disabled"})])
        form.lap.default = ""
        form.process([])

        return render_template("add_hotel.jinja2", form=form, header=header)


class UpdHotel(View):
    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, id):
        form = UpdHotelForm()
        header = make_header()

        if request.method == 'POST':
            lap_id = request.form.get('lap')
            stay = request.form.get('stay')
            phone = request.form.get('phone')
            email = request.form.get('email')
            latitude = request.form.get('geo_lat')
            longitude = request.form.get('geo_long')
            price = request.form.get('price')
            website = request.form.get('website')
            reserved = True if request.form.get('reserved') else False
            photo = None
            if 'photo' in request.files:
                file = request.files['photo']
                if file.filename != '':
                    if allowed_file(file.filename):
                        photo = secure_filename(file.filename)
                        file.save(join(current_app.config['UPLOAD_FOLDER'], 'images', photo))
                    else:
                        flash(_('Il file "%(file)s" non è una immagine ed è stato ignorato', file=file.filename),
                              category="warning")

            hotel = db.session.get(Hotel, id)
            lap = db.session.get(Lap, lap_id)

            hotel.check_in = lap.date
            hotel.check_out = hotel.check_in + timedelta(days=int(stay))
            try:
                check_hotel_date(hotel.check_in, hotel.check_out)
            except DateOverlappingError as e:
                flash(e.msg, category="error")
                laps = db.session.execute(db.select(Lap).where(
                    Lap.tour_id == db.session.execute(db.select(Tour).where(Tour.is_active)).scalar().id).order_by(Lap.date)).scalars()
                form.lap.choices = [(lap.id, f"{lap.start} - {lap.destination}", dict()) for lap in laps]
                form.lap.default = f"{hotel.lap_id}"
                form.process([])

                return render_template("upd_hotel.jinja2", form=form, hotel=hotel, timedelta=(hotel.check_out - hotel.check_in).days, header=header)

            if phone:
                hotel.phone = phone
                hotel.href_phone = ''.join(phone.split())
            if email:
                hotel.email = email
            if latitude and longitude:
                hotel.lat = latitude
                hotel.long = longitude
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
            flash(_('Hotel %(hotel)s aggiornato.', hotel=hotel.name), category="info")
            current_app.logger.info(f"Aggiornato hotel {hotel.name}.")
            return redirect(url_for("lap_bp.hotel_dashboard"))

        hotel = db.session.get(Hotel, id)
        laps = db.session.execute(db.select(Lap).where(
            Lap.tour_id == db.session.execute(db.select(Tour).where(Tour.is_active)).scalar().id).order_by(
            Lap.date)).scalars()
        form.lap.choices = [(lap.id, f"{lap.start} - {lap.destination}", dict()) for lap in laps]
        form.lap.default = f"{hotel.lap_id}"
        form.process([])

        return render_template("upd_hotel.jinja2", form=form, hotel=hotel, timedelta=(hotel.check_out - hotel.check_in).days, header=header)


class DeleteHotel(View):
    decorators = [login_required]

    def dispatch_request(self, id):
        hotel = db.session.get(Hotel, id)

        if hotel:
            if hotel.photo:
                # delete the hotel's photo
                remove(join(current_app.config['UPLOAD_FOLDER'], 'images', hotel.photo))
            db.session.delete(hotel)
            db.session.commit()
            flash(_('Cancellato albergo %(hotel)s.', hotel=hotel.name), category="info")
            current_app.logger.info(f"Cancellato albergo {hotel.name}.")

        return redirect(url_for("lap_bp.hotel_dashboard"))


class AddTour(View):
    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self):
        form = AddTourForm()

        if request.method == 'POST':
            title = request.form.get('title')
            tour_mode = request.form.get('tour_mode')
            visibility = request.form.get('visibility')
            caption = request.form.get('caption')
            cover = None
            if 'tour_cover' in request.files:
                file = request.files['tour_cover']
                if file.filename != '' and allowed_file(file.filename):
                    cover = secure_filename(file.filename)
                    file.save(join(current_app.config['UPLOAD_FOLDER'], 'images', cover))

            new_tour = Tour(
                name=title,
                trip_mode=tour_mode,
                is_visible=True if visibility == 'visible' else False,
                is_active=False,
                owner_id=session['_user_id'],
                carousel_pos=db.session.query(func.max(Tour.carousel_pos)).scalar() + 1
            )

            db.session.add(new_tour)

            if cover:
                new_tour.trip_pic = cover
            if caption:
                new_tour.pic_caption = caption

            try:
                db.session.commit()
            except IntegrityError:
                flash(_("Un viaggio con nome %(titolo)s esiste già.", titolo=title))
            else:
                user = db.session.get(Users, session['_user_id'])
                session['tours'] = len(user.tours)
                flash(_('Aggiunto viaggio "%(titolo)s".', titolo=title), category="info")
                current_app.logger.info(f"Aggiunta viaggio {title} da {user.username}")
                return redirect(url_for("start"))

        return render_template("add_tour.jinja2", form=form)


class TourManagement(View):
    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self):
        form = TourMgmtForm()

        if request.method == 'POST':
            tour = request.form.get("tour")
            visibility = request.form.get("visibility")
            caption = request.form.get("caption")
            cover = None
            if 'tour_cover' in request.files:
                file = request.files['tour_cover']
                if file.filename != '' and allowed_file(file.filename):
                    cover = secure_filename(file.filename)
                    file.save(join(current_app.config['UPLOAD_FOLDER'], 'images', cover))

            this_tour = db.session.execute(db.select(Tour).where(Tour.id == tour)).scalar()
            if visibility:
                this_tour.is_visible = True if visibility == 'visible' else False
            if cover:
                this_tour.trip_pic = cover
            if caption:
                this_tour.caption = caption

            db.session.commit()

            return redirect(url_for("start"))

        user = db.session.get(Users, session['_user_id'])

        form.tour.choices = [(tour.id, tour.name + " " + translations[tour.trip_mode], dict()) for tour in user.tours]
        form.tour.choices.extend([("", "--------", {"disabled": "disabled"})])
        form.tour.default = ""
        form.process([])

        print(url_for('dbms_bp.delete_tour'))

        header = make_header()
        return render_template('manage_tour.jinja2', form=form, header=header)


class TourDelete(View):
    methods = ['POST']
    decorators = [login_required]

    def dispatch_request(self):
        tour = db.session.get(Tour, request.form.get("tour"))
        if tour:
            db.session.delete(tour)
            db.session.commit()
            flash(_('Cancellato viaggio %(tour)s.', tour=tour.name + " " + translations[tour.trip_mode]), category="info")
            current_app.logger.info(f"Cancellato albergo {tour.name} {translations[tour.trip_mode]}.")
            session['tours'] -= 1
            if 'trip' in session.keys() and session['trip'] == tour.id:
                session.pop('trip')

        return redirect(url_for("start"))


dbms_bp.add_url_rule('/trip/add/', view_func=AddTour.as_view("add_tour"))
dbms_bp.add_url_rule('/lap/add/', view_func=AddLap.as_view("add_lap"))
dbms_bp.add_url_rule('/lap/update/<int:id>', view_func=UpdLap.as_view("update_lap"))
dbms_bp.add_url_rule('/lap/update/<int:id>/load_media', view_func=LoadLapMedia.as_view("load_lap_media"))
dbms_bp.add_url_rule('/lap/delete/<int:id>', view_func=DeleteLap.as_view('delete_lap'))
dbms_bp.add_url_rule('/media/delete/<string:media>', view_func=DeleteMedia.as_view('delete_media'))
dbms_bp.add_url_rule('/hotel/add/', view_func=AddHotel.as_view("add_hotel"))
dbms_bp.add_url_rule('/hotel/update/<int:id>', view_func=UpdHotel.as_view("update_hotel"))
dbms_bp.add_url_rule('/hotel/delete/<int:id>', view_func=DeleteHotel.as_view('delete_hotel'))
dbms_bp.add_url_rule('/tour', view_func=TourManagement.as_view('tour_mng'))
dbms_bp.add_url_rule('/tour/delete', view_func=TourDelete.as_view('delete_tour'))

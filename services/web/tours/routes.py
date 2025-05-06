from locale import setlocale, LC_ALL
from os import chdir, remove
from os.path import join, basename
from flask import current_app as app
from flask import session, redirect, render_template, request, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from . import db, get_locale
from .models import Tour, User
from .forms import SelectTripForm, UploadUserFilesForm
from flask.views import View
from flask_babel import _
from subprocess import Popen, STDOUT, PIPE
from shlex import split
from time import time
from glob import glob
from .utils import make_header, make_dd_lang, is_displayable, translations
from sqlalchemy.exc import OperationalError, ProgrammingError


ALLOWED_EXTENSIONS = {'tar.gz', 'dump'}


def allowed_file(filename):
    for extension in ALLOWED_EXTENSIONS:
        if filename.endswith(extension):
            return True

    return False


class Start(View):
    methods = ['GET', 'POST']

    def dispatch_request(self):

        form = SelectTripForm()

        if request.method == 'POST':
            trip = request.form.get('trip')
            if trip:
                if trip != 'add_tour':
                    session['trip'] = int(trip)
                else:
                    return redirect(url_for('dbms_bp.add_tour'))

        if 'locale' not in session:
            session['lang'] = 'it'
            session['locale'] = "it_IT.UTF-8"
        else:
            setlocale(LC_ALL, f"{session['locale']}")
        try:
            tours = db.session.execute(db.select(Tour).order_by(Tour.id)).scalars()
            form.trip.choices = [(tour.id, tour.name + " " + translations[tour.trip_mode], dict()) for tour in tours if is_displayable(tour)]
            form.trip.choices.extend([("", _("Scegli un viaggio"), {"disabled": "disabled"}), ("add_tour", _("Nuovo Viaggio"), {})])
            form.trip.default = ""
        except (OperationalError, ProgrammingError):
            header = make_header()
            return render_template("out_of_service.jinja2", header=header)
        form.process([])

        header = make_header()
        lang_selector = make_dd_lang(session['lang'])
        tours = db.session.execute(db.select(Tour).order_by(Tour.carousel_pos)).fetchall()
        for tour in tours:
            tour.Tour.is_displayable = is_displayable(tour.Tour)
        carousel_pos = 1
        ts = tours[:]
        for tour in tours:
            if tour.Tour.is_displayable:
                if 'trip' in session and tour.Tour.id == int(session['trip']):
                    carousel_pos = ts.index(tour) + 1
            else:
                ts.pop(ts.index(tour))

        return render_template("index.jinja2", current_locale=get_locale(), form=form, header=header, lang_selector=lang_selector, tours=tours, carousel_pos=carousel_pos)


class InitDb(View):
    def dispatch_request(self):
        res = Popen(['flask', 'create_db'], stdout=PIPE, stderr=STDOUT).wait()
        if res != 0:
            flash(_("Creazione database fallita"), category='error')
            app.logger.error(f"Database creation failed - 'create_db' exit code = {res}")
            return redirect(url_for("start"))
        admin = db.session.execute(db.select(User).where(User.is_admin)).scalar()
        if not admin:
            res = Popen(['flask', 'register_admins'], stdout=PIPE, stderr=STDOUT).wait()
            if res != 0:
                flash(_("Creazione database fallita"), category='error')
                app.logger.error(f"Database creation failed - 'register_admin' exit code = {res}")
                return redirect(url_for("start"))

        flash(_("Database inizializzato..."), category='info')
        app.logger.info("Database created")
        return redirect(url_for("start"))


class StaticFiles(View):
    def dispatch_request(self, filename=None):
        return send_from_directory(app.config['STATIC_FOLDER'], filename)


class DownloadFiles(View):
    def dispatch_request(self, filename=None):
        uploads = app.config['UPLOAD_FOLDER']
        return send_from_directory(uploads, filename)


class DownloadUserFiles(View):
    def dispatch_request(self):
        base = app.config['UPLOAD_FOLDER']
        chdir(base)
        for f in glob("./uploaded*.tar.gz"):
            remove(f)
        f_name = f"uploaded-{round(time())}.tar.gz"
        res = Popen(split(f"tar czvf {f_name} images tracks"), stdout=PIPE, stderr=STDOUT).wait()
        if res == 0:
            return send_from_directory(base, f_name)


class UploadUserFiles(View):
    methods = ['GET', 'POST']

    def dispatch_request(self):
        form = UploadUserFilesForm()

        if request.method == 'POST':
            user_file = None
            if 'user_file' in request.files:
                file = request.files['user_file']
                if file.filename != '' and allowed_file(file.filename):
                    user_file = secure_filename(file.filename)
                    file.save(join(app.config['UPLOAD_FOLDER'], user_file))

                chdir(app.config['UPLOAD_FOLDER'])
                Popen(split(f"tar xvf {user_file} -C {app.config['UPLOAD_FOLDER']}"), stdout=PIPE, stderr=STDOUT).wait()

            return redirect(url_for("start"))

        return render_template("upld_user_file.jinja2", form=form)


class DbBackup(View):
    def dispatch_request(self):
        base = app.config['UPLOAD_FOLDER']
        chdir(base)
        for f in glob("./dump*"):
            remove(f)

        f_name = f"{basename(app.config['SQLALCHEMY_DATABASE_URI'])}-{round(time())}.dump"
        with open(f"./{f_name}", 'w') as BCK:
            Popen(split(f"pg_dump {app.config['SQLALCHEMY_DATABASE_URI']}"), stdout=BCK)

        return send_from_directory(base, f_name)


class SetLanguage(View):
    def dispatch_request(self, lang='it'):
        session['lang'] = lang
        if lang == 'it':
            session['locale'] = 'it_IT.UTF-8'
            setlocale(LC_ALL, 'it_IT.UTF-8')
        elif lang == 'en':
            session['locale'] = 'en_GB.UTF-8'
            setlocale(LC_ALL, 'en_GB.UTF-8')
        return redirect(request.referrer)


app.add_url_rule('/', view_func=Start.as_view('start'))
app.add_url_rule("/init_db", view_func=InitDb.as_view("init_db"))
app.add_url_rule("/language/<string:lang>", view_func=SetLanguage.as_view("set_language"))
app.add_url_rule("/static/<path:filename>", view_func=StaticFiles.as_view("static_files"))
app.add_url_rule("/download/<path:filename>", view_func=DownloadFiles.as_view("download_files"))
app.add_url_rule("/download/user_files", view_func=DownloadUserFiles.as_view("download_user_files"))
app.add_url_rule("/download/db_backup", view_func=DbBackup.as_view("download_db_backup"))
app.add_url_rule("/upload/user_files", view_func=UploadUserFiles.as_view("upload_user_files"))

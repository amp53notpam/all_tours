from locale import setlocale, LC_ALL
from os.path import join
from flask import current_app as app, current_app
from flask import Blueprint, session, redirect, render_template, request, url_for, send_from_directory, flash
from . import db, get_locale
from .models import Tour
from .forms import SelectTripForm
from flask.views import View
from flask_babel import _
from subprocess import Popen, STDOUT, PIPE
from .utils import make_header, make_dd_lang, is_displayable, translations


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
        tours = db.session.execute(db.select(Tour).order_by(Tour.id)).scalars()
        form.trip.choices = [(tour.id, tour.name + " " + translations[tour.trip_mode], dict()) for tour in tours if is_displayable(tour)]
        form.trip.choices.extend([("", _("Scegli un viaggio"), {"disabled": "disabled"}), ("add_tour", _("Nuovo Viaggio"), {})])
        form.trip.default = ""
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
            current_app.logger.error(f"Database creation failed - 'create_db' exit code = {res}")
            return redirect(url_for("index"))
        res = Popen(['flask', 'register_admins'], stdout=PIPE, stderr=STDOUT).wait()
        if res != 0:
            flash(_("Creazione database fallita"), category='error')
            current_app.logger.error(f"Database creation failed - 'register_admin' exit code = {res}")
            return redirect(url_for("index"))

        flash(_("Database inizializzato..."), category='info')
        current_app.logger.info("Database created")
        return redirect(url_for("index"))


class StaticFiles(View):
    def dispatch_request(self, filename=None):
        return send_from_directory(app.config['STATIC_FOLDER'], filename)


class DownloadFiles(View):
    def dispatch_request(self, filename=None):
        uploads = join(current_app.root_path, app.config['UPLOAD_FOLDER'])
        return send_from_directory(uploads, filename)


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

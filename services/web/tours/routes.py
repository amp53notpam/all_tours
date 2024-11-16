from locale import setlocale, LC_ALL
from flask import current_app as app, current_app
from flask import session, make_response, redirect, render_template, request, url_for, send_from_directory, flash
from flask_babel import _, lazy_gettext as _l
from . import db
from .models import Tour
from .forms import SelectTripForm
from flask.views import View
from subprocess import Popen, STDOUT, PIPE
from .utils import make_header, make_dd_lang


class Start(View):
    methods = ['GET', 'POST']

    def dispatch_request(self):
        form = SelectTripForm()

        if request.method == 'POST':
            trip = request.form.get('trip')
            if trip:
                active_trip = db.session.execute(db.select(Tour).where(Tour.is_active==True)).fetchone()
                if active_trip:
                    active_trip.Tour.is_active = False
                    db.session.commit()
                next_active = db.session.execute(db.select(Tour).where(Tour.name==trip)).fetchone()
                next_active.Tour.is_active = True;
                db.session.commit()
                session['trip'] = trip

        if 'lang' not in session:
            session['lang'] = 'it'
            session['locale'] = "it_IT"
        tours = db.session.execute(db.select(Tour).order_by(Tour.id)).all()
        form.trip.choices = [("", _("Scegli il viaggio"), {"disabled": "disabled"})]
        form.trip.choices.extend([(tour.Tour.name, tour.Tour.name, dict()) for tour in tours])
        form.trip.default = ""
        form.process([])

        header = make_header(session['lang'])
        lang_selector = make_dd_lang(session['lang'])
        if 'trip' not in session:
            carousel_pos = 1
        else:
            carousel_pos = db.session.execute(db.select(Tour.carousel_pos).where(Tour.is_active == True)).scalar()

        return render_template("index.jinja2", form=form, header=header, lang_selector=lang_selector, carousel_pos=carousel_pos)


class InitDb(View):
    def dispatch_request(self):
        res = Popen(['flask', 'create_db'], stdout=PIPE, stderr=STDOUT).wait()
        if res != 0:
            flash(_("Creazione database fallita"), category='error')
            current_app.logger.error("Creazione database fallita - causa: 'create_db' KO")
            return redirect(url_for("index"))
        res = Popen(['flask', 'register_admins'], stdout=PIPE, stderr=STDOUT).wait()
        if res != 0:
            flash(_("Creazione database fallita"), category='error')
            current_app.logger.error("Creazione database fallita - causa: 'register_admin' KO")
            return redirect(url_for("index"))
        res = Popen(['flask', 'populate_db'], stdout=PIPE, stderr=STDOUT).wait()
        if res != 0:
            flash(_("Creazione database fallita"),category='error')
            current_app.logger.error("Creazione database fallita - causa: 'populate_db' KO")
            return redirect(url_for("index"))

        flash(_("Database inizializzato..."), category='info')
        current_app.logger.info("Database creato")
        return redirect(url_for("index"))


class StaticFiles(View):
    def dispatch_request(self, filename):
        return send_from_directory(app.config['STATIC_FOLDER'], filename)


class DownloadFiles(View):
    def dispatch_request(self, filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


class SetLanguage(View):
    def dispatch_request(self, lang):
        session['lang'] = lang
        if lang == 'it':
            session['locale'] = 'it_IT.UTF-8'
            setlocale(LC_ALL, 'it_IT.UTF-8')
        elif lang == 'en':
            session['locale'] = 'en_GB.UTF-8'
            setlocale(LC_ALL, 'en_GB.UTF-8')
        return "done"


app.add_url_rule('/', view_func=Start.as_view('start'))
app.add_url_rule("/init_db", view_func=InitDb.as_view("init_db"))
app.add_url_rule("/language/<string:lang>", view_func=SetLanguage.as_view("set_language"))
app.add_url_rule("/static/<path:filename>", view_func=StaticFiles.as_view("static_files"))
app.add_url_rule("/download/<path:filename>", view_func=DownloadFiles.as_view("download_files"))


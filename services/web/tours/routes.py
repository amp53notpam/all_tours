from locale import setlocale, LC_ALL
from flask import current_app as app
from flask import session, make_response, redirect, render_template, request, url_for, send_from_directory, flash
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
        tours = db.session.execute(db.select(Tour).order_by(Tour.id)).all()
        if session['lang'] == 'it':
            form.trip.choices = [("", "Scegli il viaggio", {"disabled": "disabled"})]
        else:
            form.trip.choices = [("", "Choose a trip", {"disabled": "disabled"})]
        form.trip.choices.extend([(tour.Tour.name, tour.Tour.name, dict()) for tour in tours])
        form.trip.default = ""
        form.process([])

        if session['lang'] == 'it':
            header = make_header('it')
            lang_selector = make_dd_lang('it')
            return render_template("index.jinja2", form=form, header=header, lang_selector=lang_selector)
        else:
            header = make_header('en')
            lang_selector = make_dd_lang('en')
            return render_template("index_en.jinja2", form=form, header=header, lang_selector=lang_selector)


class InitDb(View):
    def dispatch_request(self):
        res = Popen(['flask', 'create_db'], stdout=PIPE, stderr=STDOUT).wait()
        if res != 0:
            flash("Creazione database: 'create_db' KO   ", category='error')
            return redirect(url_for("index"))
        res = Popen(['flask', 'register_admins'], stdout=PIPE, stderr=STDOUT).wait()
        if res != 0:
            flash("Creazione database: 'register_admin' KO", category='error')
            return redirect(url_for("index"))
        res = Popen(['flask', 'populate_db'], stdout=PIPE, stderr=STDOUT).wait()
        if res != 0:
            flash("Creazione database: 'populate_db' KO", category='error')
            return redirect(url_for("index"))

        flash("Database started...", category='info')
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
            setlocale(LC_ALL, 'it_IT.UTF-8')
        elif lang == 'en':
            setlocale(LC_ALL, 'en_GB.UTF-8')
        return "done"


app.add_url_rule('/', view_func=Start.as_view('start'))
app.add_url_rule("/init_db", view_func=InitDb.as_view("init_db"))
app.add_url_rule("/language/<string:lang>", view_func=SetLanguage.as_view("set_language"))
app.add_url_rule("/static/<path:filename>", view_func=StaticFiles.as_view("static_files"))
app.add_url_rule("/download/<path:filename>", view_func=DownloadFiles.as_view("download_files"))


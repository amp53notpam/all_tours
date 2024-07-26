from flask import current_app as app
from flask import session, make_response, redirect, render_template, request, url_for, send_from_directory, flash
from . import db
from .models import Tour
from .forms import SelectTripForm
from flask.views import View
from subprocess import Popen, STDOUT, PIPE


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

        tours = db.session.execute(db.select(Tour).order_by(Tour.id)).all()
        form.trip.choices = [''] + [tour.Tour.name for tour in tours]

        return render_template("index.jinja2", form=form)


class InitDb(View):
    def dispatch_request(self):
        res = Popen(['flask', 'create_db'], stdout=PIPE, stderr=STDOUT).wait()
        if res != 0:
            flash("Creazione database: 'create_db' KO   ", category='error')
            return redirect(url_for("lap_bp.index"))
        res = Popen(['flask', 'register_admins'], stdout=PIPE, stderr=STDOUT).wait()
        if res != 0:
            flash("Creazione database: 'register_admin' KO", category='error')
            return redirect(url_for("lap_bp.index"))
        res = Popen(['flask', 'populate_db'], stdout=PIPE, stderr=STDOUT).wait()
        if res != 0:
            flash("Creazione database: 'populate_db' KO", category='error')
            return redirect(url_for("lap_bp.index"))

        flash("Database started...", category='info')
        return redirect(url_for("lap_bp.index"))


class StaticFiles(View):
    def dispatch_request(self, filename):
        return send_from_directory(app.config['STATIC_FOLDER'], filename)


class DownloadFiles(View):
    def dispatch_request(self, filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


app.add_url_rule('/', view_func=Start.as_view('start'))
app.add_url_rule("/init_db", view_func=InitDb.as_view("init_db"))
app.add_url_rule("/static/<path:filename>", view_func=StaticFiles.as_view("static_files"))
app.add_url_rule("/download/<path:filename>", view_func=DownloadFiles.as_view("download_files"))

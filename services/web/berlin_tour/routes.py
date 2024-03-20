from flask import current_app as app
from flask import make_response, redirect, render_template, request, url_for, send_from_directory, flash
from flask.views import View
from subprocess import Popen, STDOUT, PIPE


class Start(View):
    def dispatch_request(self):
        return redirect(url_for("lap_bp.index"))


class InitDb(View):
    def dispatch_request(self):
        res = Popen(['flask', 'create_db'], stdout=PIPE, stderr=STDOUT).wait()
        if res != 0:
            flash("Creazione database fallita", category='error')
            return redirect(url_for("lap_bp.index"))
        res = Popen(['flask', 'register_admins'], stdout=PIPE, stderr=STDOUT).wait()
        if res != 0:
            flash("Creazione database fallita", category='error')
            return redirect(url_for("lap_bp.index"))
        res = Popen(['flask', 'populate_db'], stdout=PIPE, stderr=STDOUT).wait()
        if res != 0:
            flash("Creazione database fallita", category='error')
            return redirect(url_for("lap_bp.index"))

        flash("Database started...", category='info')
        return redirect(url_for("lap_bp.index"))


class StaticFiles(View):
    def dispatch_request(self, filename):
        return send_from_directory(app.config['STATIC_FOLDER'], filename)


app.add_url_rule('/', view_func=Start.as_view('start'))
app.add_url_rule("/init_db", view_func=InitDb.as_view("init_db"))
app.add_url_rule("/static/<path:filename>", view_func=StaticFiles.as_view("static_files"))

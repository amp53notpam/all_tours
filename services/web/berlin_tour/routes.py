from flask import current_app as app
from flask import make_response, redirect, render_template, request, url_for, send_from_directory, flash
from subprocess import Popen, STDOUT, PIPE


@app.route('/')
def start():
    return redirect(url_for("lap_bp.index"))


@app.route('/start')
def set_up_database():
    res = Popen(['flask', 'create_db'], stdout=PIPE, stderr=STDOUT).wait()
    if res != 0:
        flash("Creazione database fallita", category='error')
        return redirect(url_for("lap_bp.index"))
    res = Popen(['flask', 'populate_db'], stdout=PIPE, stderr=STDOUT).wait()
    if res != 0:
        flash("Creazione database fallita", category='error')
        return redirect(url_for("lap_bp.index"))

    flash("Database started...", category='info')
    return redirect(url_for("lap_bp.index"))


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)

from flask import current_app as app
from flask import make_response, redirect, render_template, request, url_for, send_from_directory


@app.route('/')
def start():
    return redirect(url_for("lap_bp.index"))


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)

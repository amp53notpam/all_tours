from datetime import datetime, date
from os import walk
from re import search
from . import db
from sqlalchemy import func
from flask import session, current_app
from flask_babel import _, lazy_gettext as _l
from .models import Tour, Lap, User

translations = {'bicycling': _l('in bici'), 'walking': _l('a piedi'), 'driving': _l('in auto')}


def make_header():
    if 'trip' in session:
        # trip = db.session.execute(db.select(Tour.id).where(Tour.id == session['trip'])).scalar()
        trip = int(session['trip'])
        start = db.session.execute(db.select(Lap.start, Lap.date).
                                   where(Lap.tour_id == trip).
                                   where(Lap.date == db.session.execute(db.select(func.min(Lap.date)).where(Lap.tour_id == trip)).scalar())
                                   ).fetchone()
        end = db.session.execute(db.select(Lap.destination, Lap.date).
                                 where(Lap.tour_id == trip).
                                 where(Lap.date == db.session.execute(db.select(func.max(Lap.date)).where(Lap.tour_id == trip)).scalar())
                                 ).fetchone()
        if start and end:
            header = f"""
                <h2>{start.start} - {end.destination}</h2>
                <h4>{start.date.strftime("%d %B %Y")} - {end.date.strftime("%d %B %Y")}</h4>
            """
        else:
            header = f"""
                <h2>{db.session.get(Tour, trip).name}</h2>
                <h4>{_('Nuovo Viaggio')}</h4>
            """
    else:
        header = None

    return header


def make_dd_lang(lang):
    cap_lang = 'ITA' if lang == 'it' else 'ENG'
    dd_lang = f"""
    <div class='w3-dropdown-click w3-right'>
    <button  id="dd_btn" class="w3-button w3-theme w3-hover-theme w3-ripple" data-cur-lang={lang}>{cap_lang} <i id="dd_caret" class="fa-solid fa-caret-down"></i></button>
        <div id="dd_menu" class="w3-dropdown-content w3-bar-block w3-border w3-card-4 w3-border-theme">
            <button class="w3-bar-item w3-button w3-theme-l2 w3-hover-theme" data-lang="it">It</button>
            <button class="w3-bar-item w3-button w3-theme-l2 w3-hover-theme" data-lang="en">En</button>
        </div>
    </div>
    """
    return dd_lang


def make_short_template(full_template):
    templates_dir = None
    for root, dirs, files in walk(current_app.root_path):
        if full_template in files:
            templates_dir = root
            break

    with open(f"{templates_dir}/{full_template}") as IN, open(f"{templates_dir}/s_{full_template}", 'w') as OUT:
        copy = False
        for line in IN:
            if not copy:
                if search("\\$Begin", line):
                    copy = True
            else:
                if search("\\$End", line):
                    copy = False
                else:
                    OUT.write(line)

        return f"s_{full_template}"


def is_displayable(tour):
    if tour.is_visible:
        return True
    else:
        if '_user_id' not in session:
            return False
        else:
            user = db.session.get(User, session['_user_id'])
            if tour in user.tours or user.is_admin:
                return True
            else:
                return False


def get_trip():
    return db.session.execute(db.select(Tour).where(Tour.id == int(session['trip']))).scalar()

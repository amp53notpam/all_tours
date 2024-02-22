import os
from datetime import datetime, time
import logging
from logging.handlers import RotatingFileHandler

from locale import LC_ALL, setlocale
from json import load

import sqlalchemy as sa
from click import echo

from flask import Flask
from flask.logging import default_handler
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)

    config_type = os.getenv('CONFIG_TYPE', default='DevelopmentConfig')
    if test_config is None:
        app.config.from_object(f"config.{config_type}")
    else:
        app.config.from_mapping(test_config)

    initialize_extensions(app)
    register_blueprints(app)
    configure_logging(app)
    register_cli_commands(app)

    return app


# Helper functions
def initialize_extensions(app):
    # Since the application instance is now created, pass it to each Flask
    # extension instance to bind it to the Flask application instance (app)
    db.init_app(app)


def register_blueprints(app):
    # Since the application instance is now created, register each Blueprint
    # with the Flask application instance (app)

    with app.app_context():
        # Include our Routes
        from . import routes

        # Register Blueprints
        from berlin_tour.laps import laps
        app.register_blueprint(laps.lap_bp)


def configure_logging(app):
    if app.config['LOG_WITH_GUNICORN']:
        gunicorn_error_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers.extend(gunicorn_error_logger.handlers)
        app.logger.setLevel(logging.DEBUG)
    else:
        file_handler = RotatingFileHandler('instance/flask-user-management.log',
                                           maxBytes=16384,
                                           backupCount=20)
        file_formatter = logging.Formatter('%(asctime)s %(levelname)s %(threadName)s-%(thread)d: %(message)s [in %(filename)s:%(lineno)d]')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    # Remove the default logger configured by Flask
    app.logger.removeHandler(default_handler)

    app.logger.info('Starting the Flask Berlin Tour App...')


def populate_db():
    """ Populate the database """
    from berlin_tour.models import Lap, Hotel

    setlocale(LC_ALL, 'it_IT.UTF-8')

    with open("berlin_tour/progetto.json") as IN:
        laps = load(IN)

    for lap in laps:
        new_hotel = Hotel(name=lap['Alloggio'],
                          address=lap['Indirizzo'],
                          town=lap['End'],
                          check_in=datetime.strptime(lap['Check-in'], "%a %d %b %Y").date(),
                          check_out=datetime.strptime(lap['Check-out'], "%a %d %b %Y").date(),
                          price=lap['Costo'],
                          photo=lap['Photo'],
                          link=lap['Booking']
                          )
        new_hotel.laps = [Lap(date=datetime.strptime(lap['Data'], "%a %d %b %Y").date(),
                              start=lap['Start'],
                              destination=lap['End'],
                              distance=lap['Distanza'],
                              ascent=lap['Ascesa'],
                              descent=lap['Discesa'],
                              duration=time.fromisoformat(lap['Tempo']),
                              gpx=lap['gpx']
                              )
                          ]

        db.session.add(new_hotel)
        db.session.commit()


def register_cli_commands(app):

    @app.cli.command('create_db')
    def create_db():
        """Create the database. """
        with app.app_context():
            db.drop_all()
            db.create_all()
            echo('Created the database')

    @app.cli.command('populate_db')
    def populate_db():
        """ Populate the database """
        from berlin_tour.models import Lap, Hotel

        setlocale(LC_ALL, 'it_IT.UTF-8')

        with open("berlin_tour/progetto.json") as IN:
            laps = load(IN)

        with app.app_context():
            for lap in laps:
                new_hotel = Hotel(name=lap['Alloggio'],
                                  address=lap['Indirizzo'],
                                  town=lap['End'],
                                  check_in=datetime.strptime(lap['Check-in'], "%a %d %b %Y").date(),
                                  check_out=datetime.strptime(lap['Check-out'], "%a %d %b %Y").date(),
                                  price=lap['Costo'],
                                  photo=lap['Photo'],
                                  link=lap['Booking']
                                  )
                new_hotel.laps = [Lap(date=datetime.strptime(lap['Data'], "%a %d %b %Y").date(),
                                      start=lap['Start'],
                                      destination=lap['End'],
                                      distance=lap['Distanza'],
                                      ascent=lap['Ascesa'],
                                      descent=lap['Discesa'],
                                      duration=time.fromisoformat(lap['Tempo']),
                                      gpx=lap['gpx']
                                      )
                                  ]
                db.session.add(new_hotel)
                db.session.commit()
        echo('The database has been populated')

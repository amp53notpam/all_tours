import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)

    if test_config is None:
        app.config.from_object('config.Config')
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)

    with app.app_context():

        # Include our Routes
        from . import routes

        # Register Blueprints
        from .laps import laps
        app.register_blueprint(laps.lap_bp)

        return app

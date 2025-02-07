import os
from datetime import datetime, time
import logging
from logging.handlers import RotatingFileHandler
from click import echo
from flask import Flask, session, request, current_app
from flask.logging import default_handler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_session import Session
from flask_babel import Babel
from flask_mail import Mail
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from werkzeug.security import generate_password_hash


class Base(DeclarativeBase, MappedAsDataclass):
    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
login_manager = LoginManager()
sess = Session()
babel = Babel()
mail = Mail()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)

    config_type = os.getenv('CONFIG_TYPE', default='DevelopmentConfig')
    if test_config is None:
        app.config.from_object(f"config.{config_type}")
    else:
        app.config.from_mapping(test_config)

    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(app.instance_path), 'uploaded')

    initialize_extensions(app)
    register_blueprints(app)
    configure_logging(app)
    configure_upload_area(app)
    register_cli_commands(app)

    return app


def get_locale():
    try:
        return session.get("lang", "it")
    except RuntimeError:
        return "it"


# Helper functions
def initialize_extensions(app):
    # Since the application instance is now created, pass it to each Flask
    # extension instance to bind it to the Flask application instance (app)
    db.init_app(app)
    migrate.init_app(app, db)
    sess.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth_bp.login'
    login_manager.init_app(app)

    from .models import Users

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Users, int(user_id))

    babel.init_app(app, default_locale='it', locale_selector=get_locale)


def register_blueprints(app):
    # Since the application instance is now created, register each Blueprint
    # with the Flask application instance (app)

    with app.app_context():
        # Include our Routes
        from . import routes

        # Register Blueprints
        from tours.laps import laps
        app.register_blueprint(laps.lap_bp)

        from tours.auth import auth
        app.register_blueprint(auth.auth_bp)

        from tours.dbms import dbms
        app.register_blueprint(dbms.dbms_bp)

        from tours.maps import maps
        app.register_blueprint(maps.map_bp)


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


def configure_upload_area(app):
    try:
        os.mkdir(f"{app.config['UPLOAD_FOLDER']}/tracks")
        app.logger.info("Creato sub-folder 'tracks' in 'uploaded")
    except FileExistsError:
        pass

    try:
        os.mkdir(f"{app.config['UPLOAD_FOLDER']}/images")
        app.logger.info("Creato sub-folder 'images' in 'uploaded")
    except FileExistsError:
        pass


def register_cli_commands(app):

    @app.cli.command('create_db')
    def create_db():
        """Create the database. """
        with app.app_context():
            db.drop_all()
            db.create_all()
            echo('Database created')

    @app.cli.command('register_admins')
    def register_admins():
        """ Create the database admins"""
        from .models import Users

        with app.app_context():
            admins = [{'username': 'tourAdmin', 'password': generate_password_hash('Santiago2024!'), 'email': 'admin@tours.org', 'is_admin': True}
                      ]
            db.session.bulk_insert_mappings(Users, admins)
            db.session.commit()

from os import environ, path
from dotenv import load_dotenv
from datetime import timedelta
from tours import db


load_dotenv('.env.pg')


class DevelopmentConfig:
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True

    SECRET_KEY = environ.get('SECRET_KEY')
    STATIC_FORLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    # Database
    SQLALCHEMY_DATABASE_URI = f"{environ.get('DATABASE')}://\
                                {environ.get('POSTGRES_USER')}:{environ.get('POSTGRES_PASSWORD')}@\
                                {environ.get('POSTGRES_HOST')}:{environ.get('POSTGRES_PORT')}/\
                                {environ.get('POSTGRES_DB')}".replace(" ", "")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Logging
    LOG_WITH_GUNICORN = True

    # server-side sessions from flask-session
    SESSION_TYPE = "sqlalchemy"
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)
    SESSION_SERIALIZATION_FORMAT = "msgpack"
    SESSION_SQLALCHEMY = db
    SESSION_SQLALCHEMY_TABLE = 'tour_session'

    # SMTP
    MAIL_SERVER = "out.virgilio.it"
    MAIL_PORT = 465
    MAIL_USERNAME = "apozzi53@virgilio.it"
    MAIL_PASSWORD = "aC2yak36ZJ!"
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_SUPPRESS_SEND = False

    # internationalization
    BABEL_DEFAULT_LOCALE = 'it'
    LANGUAGES = ['it', 'en']


class ProductionConfig(DevelopmentConfig):
    FLASK_ENV = 'production'

    DEBUG = False
    TESTING = False

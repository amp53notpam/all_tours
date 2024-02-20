from os import environ, path
from dotenv import load_dotenv


load_dotenv('.env')


class DevelopmentConfig:
    FLASK_ENV = 'development'
    DEBUG = True if FLASK_ENV == 'development' else False
    TESTING = True if FLASK_ENV == 'development' else False

    SECRET_KEY = environ.get('SECRET_KEY')
    STATIC_FORLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Logging
    LOG_WITH_GUNICORN = environ.get('LOG_WITH_GUNICORN', default=False)


class ProductionConfig(DevelopmentConfig):
    FLASK_ENV = 'production'

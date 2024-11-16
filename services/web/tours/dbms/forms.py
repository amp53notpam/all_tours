from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from flask_wtf.file import FileField, MultipleFileField, FileRequired, FileAllowed
from wtforms import StringField, IntegerField, FloatField, SubmitField, URLField, BooleanField, EmailField, TelField
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms.validators import DataRequired


class AddLapForm(FlaskForm):
    date = StringField(_l('Data della tappa'), validators=[DataRequired()])
    start = StringField(_l('Partenza'), validators=[DataRequired()])
    destination = StringField(_l('Arrivo'), validators=[DataRequired()])
    distance = FloatField(_l('Distanza'))
    ascent = IntegerField(_l('Dislivello salita'))
    descent = IntegerField(_l('Dislivello discesa'))
    duration = StringField(_l('Tempo previsto'))
    gpx = FileField(_l("Traccia gpx (.gpx)"), validators=[FileAllowed(['gpx'])])
    submit = SubmitField('OK')


class UpdLapForm(FlaskForm):
    date = StringField(_l('Data della tappa'), validators=[DataRequired()])
    distance = FloatField(_l('Distanza'))
    ascent = IntegerField(_l('Dislivello salita'))
    descent = IntegerField(_l('Dislivello discesa'))
    duration = StringField(_l('Tempo'))
    gpx = FileField(_l("Traccia gpx (.gpx)"), validators=[FileAllowed(['gpx'])])
    photos = MultipleFileField(_l('Foto'), validators=[FileAllowed(['jpg', 'jpeg', 'mov'])])
    done = BooleanField(_l('OK è fatta!'))
    submit = SubmitField('OK')


class AddHotelForm(FlaskForm):
    name = StringField(_l('Albergo'), validators=[DataRequired()])
    address = StringField(_l('Indirizzo'), validators=[DataRequired()])
    town = StringField(_l('Città'), validators=[DataRequired()])
    geo_lat = FloatField("Lat. & Long.")
    geo_long = FloatField()
    email = EmailField("E-mail")
    phone = TelField(_l('Telefono'))
    check_in = StringField(_l('Data check-in'))
    check_out = StringField(_l('Data check-out'))
    price = FloatField(_l('Costo'))
    photo = FileField(_l("Foto dell'albergo"), validators=[FileAllowed(['webp', 'jpg', 'jpeg'])])
    website = URLField(_l("Sito web"))
    reserved = BooleanField(_l('È prenotato'))
    submit = SubmitField('OK')


class UpdHotelForm(FlaskForm):
    email = EmailField("E-mail")
    phone = TelField(_l('Telefono'))
    geo_lat = FloatField("Lat. & Long.")
    geo_long = FloatField()
    check_in = StringField(_l('Data check-in'))
    check_out = StringField(_l('Data check-out'))
    price = FloatField(_l('Costo'))
    photo = FileField(_l("Foto dell'albergo"), validators=[FileAllowed(['webp', 'jpg', 'jpeg'])])
    website = URLField(_l("Sito web"))
    reserved = BooleanField(_l('È prenotato'))
    submit = SubmitField('OK')

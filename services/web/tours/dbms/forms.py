from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from flask_wtf.file import FileField, MultipleFileField, FileRequired, FileAllowed
from wtforms import StringField, IntegerField, FloatField, SubmitField, URLField, BooleanField, EmailField, TelField, RadioField, SelectField, DateField, TimeField, validators
from wtforms.validators import DataRequired, Email


class AddLapForm(FlaskForm):
    date = DateField(_l('Data della tappa'))
    start = StringField(_l('Partenza'))
    destination = StringField(_l('Arrivo'))
    distance = FloatField(_l('Distanza'))
    ascent = IntegerField(_l('Dislivello salita'))
    descent = IntegerField(_l('Dislivello discesa'))
    duration = TimeField(_l('Tempo previsto'))
    gpx = FileField(_l("Traccia gpx (.gpx)"), validators=[FileAllowed(['gpx'])])
    submit = SubmitField('OK')


class UpdLapForm(FlaskForm):
    date = DateField(_l('Data della tappa'))
    distance = FloatField(_l('Distanza'))
    ascent = IntegerField(_l('Dislivello salita'))
    descent = IntegerField(_l('Dislivello discesa'))
    duration = TimeField(_l('Tempo'))
    gpx = FileField(_l("Traccia gpx (.gpx)"), validators=[FileAllowed(['gpx'])])
    done = BooleanField(_l('OK è fatta!'))
    submit = SubmitField('OK')


class LoadMediaForm(FlaskForm):
    media_file = FileField(_l('File'), validators=[FileAllowed(['jpg', 'jpeg', 'mov', 'mp4'])])
    caption = StringField(_l('Didascalia'))
    submit = SubmitField('OK')


class AddHotelForm(FlaskForm):
    name = StringField(_l('Albergo'))
    address = StringField(_l('Indirizzo'))
    town = StringField(_l('Città'))
    lap = SelectField(_l('Tappa'))
    stay = IntegerField(_l('Giorni di soggiorno'))
    geo_lat = FloatField("Lat. & Long.")
    geo_long = FloatField()
    email = EmailField("E-mail", validators=[Email(message=_l('E-mail non valida'))])
    phone = TelField(_l('Telefono'))
    price = FloatField(_l('Costo'))
    photo = FileField(_l("Foto dell'albergo"), validators=[FileAllowed(['webp', 'jpg', 'jpeg'])])
    website = URLField(_l("Sito web"))
    reserved = BooleanField(_l('È prenotato'))
    submit = SubmitField('OK')


class UpdHotelForm(FlaskForm):
    lap = SelectField(_l('Tappa'))
    stay = IntegerField(_l('Giorni di soggiorno'))
    email = EmailField("E-mail")
    phone = TelField(_l())
    phone_action = RadioField(_l('Telefono'), choices=[('add', _l('Aggiungi')), ('delete', _l('Cancella'))], default='add')
    geo_lat = FloatField("Lat. & Long.")
    geo_long = FloatField()
    price = FloatField(_l('Costo'))
    photo = FileField(_l("Foto dell'albergo"), validators=[FileAllowed(['webp', 'jpg', 'jpeg'])])
    website = URLField(_l("Sito web"))
    reserved = BooleanField(_l('È prenotato'))
    submit = SubmitField('OK')


class AddTourForm(FlaskForm):
    # title = StringField(_l('Titolo del Viaggio'), validators=[DataRequired()])
    title = StringField(_l('Titolo del Viaggio'))
    tour_mode = RadioField(_l('Tipo di Viaggio'), choices=[('walking', _l('a piedi')), ('bicycling', _l('in bicicletta')), ('driving', _l('in auto'))], default='walking')
    visibility = RadioField(_l('Visibilità'), choices=[('visible', _l('Totale')), ('hidden', _l('Ristretta'))], default='visible')
    tour_cover = FileField(_l('Copertina'), validators=[FileAllowed(['jpg', 'jpeg'])])
    # caption = StringField(_l('Didascalia'), [validators.length(max=96)])
    caption = StringField(_l('Didascalia'))
    submit = SubmitField('OK')


class TourMgmtForm(FlaskForm):
    tour = SelectField(_l("Viaggio"))
    visibility = RadioField(_l('Visibilità'), choices=[('visible', _l('Totale')), ('hidden', _l('Ristretta'))])
    tour_cover = FileField(_l('Copertina'), validators=[FileAllowed(['jpg', 'jpeg'])])
    caption = StringField(_l('Didascalia'))
    submit = SubmitField('Modifica')
    submit_del = SubmitField(_l('Cancella'))

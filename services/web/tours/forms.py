from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms import SelectField, SubmitField, widgets


class SelectTripForm(FlaskForm):
    trip = SelectField(lazy_gettext("Scegli il viaggio"))
    submit = SubmitField('OK')

from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import SelectField, SubmitField, widgets


class SelectTripForm(FlaskForm):
    trip = SelectField(_l("Scegli il viaggio"))
    submit = SubmitField('OK')
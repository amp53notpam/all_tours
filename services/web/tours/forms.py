from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, widgets


class SelectTripForm(FlaskForm):
    trip = SelectField("Scegli il viaggio")
    submit = SubmitField('OK')
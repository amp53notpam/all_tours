from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import EmailField, PasswordField, SubmitField, BooleanField, SelectField, widgets
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms.validators import InputRequired, Email


class InputRequired0(InputRequired):
    def __init__(self, message=None):
        super().__init__(message=message)
        self.field_flags = {"required": False}


class LogInForm(FlaskForm):
    email = EmailField("", [InputRequired0(message=_l("E-mail non inserita."))])
    password = PasswordField('Password', [InputRequired0(message=_l("Password non inserita."))])
    remember = BooleanField(_l('Ricordami'))
    submit = SubmitField('Login')

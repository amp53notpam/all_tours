from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import EmailField, PasswordField, SubmitField, BooleanField
from wtforms.fields.simple import StringField
from wtforms.validators import Email, EqualTo


class LogInForm(FlaskForm):
    username = StringField("Username")
    password = PasswordField('Password')
    remember = BooleanField(_l('Ricordami'))
    submit = SubmitField('Login')


class SignUpForm(FlaskForm):
    username = StringField("Username")
    password = PasswordField('Password', [EqualTo('vfy_password', message=_l('Le passwords non coincidono'))])
    vfy_password = PasswordField(_l('Conferma'))
    email = EmailField("E-mail", [Email(message=_l('E-mail non valida'))])
    submit = SubmitField(_l('Registrami'))


class LostPasswordForm(FlaskForm):
    username = StringField("Username")
    submit = SubmitField(_l('Invia'))


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField(_l('Nuova Password'), [EqualTo('vfy_password', message=_l('Le passwords non coincidono'))])
    vfy_password = PasswordField(_l('Conferma'))
    submit = SubmitField(_l('Invia'))

from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import SelectField, SubmitField, widgets
from flask_wtf.file import FileField, FileAllowed


class SelectTripForm(FlaskForm):
    trip = SelectField(_l("Scegli il viaggio"))
    submit = SubmitField('OK')


class UploadUserFilesForm(FlaskForm):
    user_file = FileField('File', validators=[FileAllowed(['tar.gz'])])
    submit = SubmitField('OK')

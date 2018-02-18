import wtforms
from wtforms import validators
import flask_wtf
from flask_wtf.file import FileField


class UploadForm(flask_wtf.FlaskForm):
    file = wtforms.FileField(
        'Journal File', validators=[validators.Required()])

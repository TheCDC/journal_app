import flask_wtf
from flask_wtf.file import FileField, FileRequired


class UploadForm(flask_wtf.FlaskForm):
    file = FileField('Journal File', validators=[FileRequired()])

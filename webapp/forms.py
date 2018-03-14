import flask_wtf
from flask_wtf.file import FileField, FileRequired
import wtforms
import wtforms.validators


class UploadForm(flask_wtf.FlaskForm):
    file = FileField('Journal File', validators=[FileRequired()])


class ContentsSearchForm(flask_wtf.FlaskForm):
    query = wtforms.StringField(validators=[wtforms.validators.DataRequired()])

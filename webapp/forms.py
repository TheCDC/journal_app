import flask_wtf
from flask_wtf.file import FileField, FileRequired
import wtforms
import wtforms.validators


class UploadForm(flask_wtf.FlaskForm):
    file = FileField('Journal File', validators=[FileRequired()])


class ContentsSearchForm(flask_wtf.FlaskForm):
    query = wtforms.StringField(validators=[wtforms.validators.DataRequired()])


class LoginForm(flask_wtf.FlaskForm):
    username = wtforms.StringField(
        validators=[wtforms.validators.DataRequired()])
    password = wtforms.StringField(
        validators=[wtforms.validators.DataRequired()])


class RegisterForm(LoginForm):
    email = wtforms.StringField(validators=[wtforms.validators.DataRequired()])
    first_name = wtforms.StringField(
        validators=[wtforms.validators.DataRequired()])
    last_name = wtforms.StringField(
        validators=[wtforms.validators.DataRequired()])

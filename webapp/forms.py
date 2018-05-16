import flask_wtf
from flask_wtf.file import FileField, FileRequired
import wtforms
import wtforms.fields.html5
import wtforms.validators


class UploadForm(flask_wtf.FlaskForm):
    file = FileField('Journal File', validators=[FileRequired()])


class ContentsSearchForm(flask_wtf.FlaskForm):
    query = wtforms.StringField(validators=[wtforms.validators.DataRequired()])


class LoginForm(flask_wtf.FlaskForm):
    username = wtforms.StringField(
        validators=[wtforms.validators.DataRequired()])
    # https://wtforms.readthedocs.io/en/latest/validators.html
    password = wtforms.PasswordField(
        validators=[wtforms.validators.DataRequired()])


class RegisterForm(LoginForm):
    password_confirm = wtforms.PasswordField(validators=[
        wtforms.validators.DataRequired(),
        wtforms.validators.EqualTo(
            'password', message='Passwords must match!')
    ])
    email = wtforms.fields.html5.EmailField(
        'New email address', validators=[wtforms.validators.DataRequired()])
    first_name = wtforms.StringField(
        validators=[wtforms.validators.DataRequired()])
    last_name = wtforms.StringField(
        validators=[wtforms.validators.DataRequired()])


class AccountSettingsForm(flask_wtf.FlaskForm):
    password = wtforms.PasswordField('Old password', validators=[])
    new_password = wtforms.PasswordField(validators=[])
    new_password_confirm = wtforms.PasswordField(validators=[])
    first_name = wtforms.StringField('First name', validators=[])
    last_name = wtforms.StringField('Last name', validators=[])
    email = wtforms.fields.html5.EmailField('New email address', validators=[])

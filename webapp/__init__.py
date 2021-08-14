import flask
import os
import logging.config
from webapp import config
import flask_login

logger = logging.getLogger(__name__)
#  ========== Flask App ==========
app = flask.Flask(
    __name__, static_url_path='/static', template_folder=config.tmpl_dir)
# auto reload template engine when template files change
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
key = os.environ.get('SECRET_KEY', None)
if key is None:
    raise RuntimeError('App SECRET_KEY must be provided in env vars!')
app.config['SECRET_KEY'] = key
app.config[
    'SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
# ========== Flask-Security config ==========
app.config.update(dict(
    SECURITY_PASSWORD_SALT=os.environ.get('SECURITY_PASSWORD_SALT', None),
    SECURITY_REGISTER_URL='/register',
    SECURITY_LOGIN_URL='/login',
    SECURITY_LOGOUT_URL='/logout',
    SECURITY_CHANGE_URL='/change_password',

    SECURITY_CHANGEABLE=True,
    SECURITY_REGISTERABLE=True,
    SECURITY_CONFIRMABLE=False,
    SECURITY_SEND_REGISTER_EMAIL=False,
    SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL=False,
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL=False,
))

print(app.url_map)

from . import models

# ========== Setup flask-login ==========
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'security.login'
login_manager.login_view = 'security.register'


@login_manager.user_loader
def load_user(target_id: int) -> models.User:
    return models.User.query.filter_by(id=int(target_id)).first()


@app.before_first_request
def setup_app():
    from webapp import models
    # models.instantiate_db(app)


from . import views

views.add_views(app)


import webapp.journal_plugins

webapp.journal_plugins.extensions.plugin_manager.init_app(app,
                                                          view_func=webapp.journal_plugins.views.ExampleView.as_view(
                                                              'plugins-index'))



def main():
    logger.info('run app')
    app.run(debug=True)
    print(app.url_map)

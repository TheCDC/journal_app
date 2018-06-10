import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_bootstrap
import flask_login
import flask_mail
from flask_marshmallow import Marshmallow
# for editing DB entries
from flask_admin import Admin
import logging
from . import config
import os

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

# ========== Setup sqlalchemy ==========
db = SQLAlchemy(app)
# ========== Setup flask-marshmallow ==========
marshmallow = Marshmallow(app)
# initialize migration engine
migrate = Migrate(app, db, directory=config.ALEMBIC_PATH)
# ========== Setup flask-mail ==========
mail = flask_mail.Mail(app)

# ========== Setup flask-admin ==========
if config.DEBUG_ENABLED:
    admin = Admin(app, name='Journal Wiki App', template_mode='bootstrap3')
else:
    admin = None
# ========== Setup Bootstrap ==========
bootstrap = flask_bootstrap.Bootstrap(app)
# ========== Setup flask-login ==========
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ==========  Journal Parsing Plugins ==========
from webapp.journal_plugins import PluginManager
plugin_manager = PluginManager(app)
from webapp.journal_plugins import example_plugin
example_plugin = example_plugin.Plugin(plugin_manager)
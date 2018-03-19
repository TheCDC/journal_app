import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_bootstrap
import flask_login
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

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{config.SQLITE_DB_PATH}'
# initialize SQLAlchemy engine
db = SQLAlchemy(app)
# initialize migration engine
migrate = Migrate(app, db, directory=config.ALEMBIC_PATH)
# admin interface
if config.DEBUG_ENABLED:
    admin = Admin(app, name='Journal Wiki App', template_mode='bootstrap3')
else:
    admin = None
# bootstrap
bootstrap = flask_bootstrap.Bootstrap(app)
# logins
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.logiin_view = 'login'

import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_bootstrap
# for editing DB entries
from flask_admin import Admin
import random
import os
import logging

CONFIG_PATH = os.path.expanduser(os.path.join('~/', 'cdc_journal'))
#  ========== Logging ==========

LOG_PATH = os.path.join(CONFIG_PATH, 'journal_app.log')

logger = logging.getLogger(__name__)
logger.debug('importing plugins')

#  ========== Paths ==========
# hack to get a reference to the templates directory within the package
tmpl_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'templates')
ALEMBIC_PATH = os.path.join(CONFIG_PATH, 'migrations')
# set the database location and protocol
SQLITE_DB_PATH = os.path.join(CONFIG_PATH, 'database.db')
try:
    os.makedirs(os.path.dirname(SQLITE_DB_PATH))
except FileExistsError:
    pass

#  ========== Flask App ==========
app = flask.Flask(
    __name__, static_url_path='/static', template_folder=tmpl_dir)
# auto reload template engine when template files change
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = str(int(random.random() * 100000000000))

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{SQLITE_DB_PATH}'
# initialize SQLAlchemy engine
db = SQLAlchemy(app)
# initialize migration engine
migrate = Migrate(app, db)
# admin interface
admin = Admin(app, name='Journal Wiki App', template_mode='bootstrap3')

bootstrap = flask_bootstrap.Bootstrap(app)

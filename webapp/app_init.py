import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_bootstrap
# for editing DB entries
from flask_admin import Admin
import random
import logging
from . import config

logger = logging.getLogger(__name__)
#  ========== Flask App ==========
app = flask.Flask(
    __name__, static_url_path='/static', template_folder=config.tmpl_dir)
# auto reload template engine when template files change
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = str(int(random.random() * 100000000000))

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{config.SQLITE_DB_PATH}'
# initialize SQLAlchemy engine
db = SQLAlchemy(app)
# initialize migration engine
migrate = Migrate(app, db)
# admin interface
admin = Admin(app, name='Journal Wiki App', template_mode='bootstrap3')

bootstrap = flask_bootstrap.Bootstrap(app)

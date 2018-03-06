import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
import random
# for editing DB entries
# hack to get a reference to the templates directory within the package
import os
print('importing plugins')

tmpl_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'templates')

#  ========== Flask App ==========
app = flask.Flask(
    __name__, static_url_path='/static', template_folder=tmpl_dir)
# auto reload template engine when template files change
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = str(int(random.random() * 100000000000))
# set the database location and protocol
sqlite_db_path = os.path.expanduser(
    os.path.join('~/', 'cdc_journal', 'database.db'))
try:
    os.makedirs(os.path.dirname(sqlite_db_path))
except FileExistsError:
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_db_path}'
# initialize SQLAlchemy engine
db = SQLAlchemy(app)
# initialize migration engine
migrate = Migrate(app, db)
# admin interface
admin = Admin(app, name='Journal Wiki App', template_mode='bootstrap3')
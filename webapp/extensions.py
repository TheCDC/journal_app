from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_bootstrap
import flask_mail
from flask_marshmallow import Marshmallow
# for editing DB entries
from flask_admin import Admin
from webapp import config
import webapp
from webapp import app



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

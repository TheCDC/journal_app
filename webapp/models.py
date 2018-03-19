from webapp.app_init import app, db, admin
import webapp.app_init
from flask_admin.contrib.sqla import ModelView
import datetime
from webapp import parsing
import logging
import flask_migrate
import alembic
logger = logging.getLogger(__name__)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, index=True)
    password = db.Column(db.String)
    email = db.Column(db.String, unique=True, index=True)
    registered_on = db.Column(db.DateTime)


class JournalEntry(db.Model):
    """Model for journal entries."""
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    contents = db.Column(db.String)

    def __str__(self):
        return str(self.id)

    def to_html(self) -> str:
        """Return HTML necesary to render the entry the same as plain text."""
        return self.contents.replace('\n', '<br>')

    @property
    def tokens(self):
        """Return the contents parsed as tokens."""
        raise NotImplementedError(
            'TODO: tokenize entry contents to allow for wiki-style linking.')

    @property
    def date_string(self) -> str:
        """Date as YYYY-MM-DD."""
        return self.create_date.strftime('%Y-%m-%d')

    @property
    def date_human(self) -> str:
        """A pretty and human readable date."""
        return self.create_date.strftime('%B %d, %Y')


class PluginConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    class_name = db.Column(db.String)
    enabled = db.Column(db.Boolean, default=True)
    name = db.Column(db.String)


class JournalEntryView(ModelView):
    column_list = (
        'create_date',
        'contents',
    )

    def summary(view, context, model, name):
        s = model.contents
        return s[:30] + (len(s) > 30) * '...'

    column_formatters = {
        'contents': summary,
    }


admin.add_view(
    JournalEntryView(
        JournalEntry, db.session, endpoint='model_view_journalentry'))
admin.add_view(
    ModelView(PluginConfig, db.session, endpoint='model_view_pluginconfig'))


def instantiate_db(app):
    """Make sure the db is initialized."""
    # initialize db with flask_migrate
    with app.app_context():
        try:
            flask_migrate.init(webapp.config.ALEMBIC_PATH)
        except alembic.util.exc.CommandError as e:
            if 'already exists' in str(e):
                pass
            else:
                logger.debug('flask db init failed: %s', e)
                raise e
        flask_migrate.migrate(webapp.config.ALEMBIC_PATH)
        try:
            logger.debug('flask db upgrade')
            flask_migrate.upgrade(webapp.config.ALEMBIC_PATH)
        except Exception as e:
            logger.debug('flask db upgrade failed: %s', e)
            raise e

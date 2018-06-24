from webapp.api import link_for_entry
from webapp.extensions import db, admin, marshmallow
from webapp import app
from webapp import config
import webapp
from flask_admin.contrib.sqla import ModelView
import datetime
import logging
import flask_migrate
import alembic
import markdown
from flask_security import UserMixin, RoleMixin
from flask_security import Security, SQLAlchemyUserDatastore
from sqlalchemy.orm import backref
from sqlalchemy.sql import func


logger = logging.getLogger(__name__)

# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(),
                                 db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(),
                                 db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, index=True)
    password = db.Column(db.String(200))
    email = db.Column(db.String(200), unique=True, index=True)
    registered_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic'))

    # ========== flask-login methods ==========
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def get_latest_entry(self, ) -> "JournalEntry":
        """Return the chronologically latest JournalEntry."""
        # session = db.session()
        # session.add(self)
        return JournalEntry.query.filter(JournalEntry.owner_id == self.id).order_by(
            JournalEntry.create_date.desc()).first()

    def query_all_entries(self):
        return JournalEntry.query.filter(JournalEntry.owner_id == self.id)

    def get_all_years(self, ) -> 'iterable[datetime.datetime]':
        """Return a list of dates corresponding to the range of
        years encompassed by all journal entries."""
        # define earliest and latest years of entries
        start_year = self.query_all_entries().order_by(
            JournalEntry.create_date).first()
        end_year = self.query_all_entries().order_by(
            JournalEntry.create_date.desc()).first()
        if start_year and end_year:
            for y in range(start_year.create_date.year,
                           end_year.create_date.year + 1):
                # find any entry within this year but before next year
                found = self.query_all_entries().filter(
                    JournalEntry.create_date >= datetime.datetime(
                        y, 1, 1, 0, 0)).filter(
                    JournalEntry.create_date < datetime.datetime(
                        y + 1, 1, 1, 0, 0)).first()
                # only yield this year if has an entry
                if found:
                    yield datetime.datetime(y, 1, 1, 0, 0)

    def next_entry(self, e: "JournalEntry") -> "JournalEntry":
        """Return the first JournalEntry that falls chronologically after
        the given entry."""
        return self.query_all_entries().filter(
            JournalEntry.create_date > e.create_date).first()

    def previous_entry(self, e: "JournalEntry") -> "JournalEntry":
        """Return the first JournalEntry that falls chronologically before
        the given entry."""
        return self.query_all_entries().filter(
            JournalEntry.create_date < e.create_date).order_by(
            JournalEntry.create_date.desc()).first()


class JournalEntry(db.Model):
    """Model for journal entries."""
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(
        db.Date, default=func.now(), index=True)
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now(), nullable=False,
        server_default=func.now())
    contents = db.Column(db.String)
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id,ondelete="cascade"))
    owner = db.relationship(User, backref=backref('entries', cascade="all,delete"), )
    __table_args__ = (db.UniqueConstraint('owner_id', 'create_date', name='_id_date'),)

    def __str__(self):
        return repr(self.id)

    def __repr__(self):
        return f'< JournaEntry id={self.id} create_date={self.create_date}'

    @property
    def html(self) -> str:
        """Return HTML rendering of markdown contents."""
        return markdown.markdown(self.contents)

    @property
    def date_string(self) -> str:
        """Date as YYYY-MM-DD."""
        return self.create_date.strftime('%Y-%m-%d')

    @property
    def date_human(self) -> str:
        """A pretty and human readable date."""
        return self.create_date.strftime('%B %d, %Y, a %A')

    @property
    def next(self):
        found = JournalEntry.query.filter(JournalEntry.owner_id == self.owner_id).order_by(
            JournalEntry.create_date).filter(
            JournalEntry.create_date > self.create_date).first()
        if found:
            if found.id != self.id:
                return found
        return None

    @property
    def previous(self):

        found = JournalEntry.query.filter(JournalEntry.owner_id == self.owner_id).filter(
            JournalEntry.create_date < self.create_date).order_by(
            JournalEntry.create_date.desc()).first()

        if found:
            if found.id != self.id:
                return found
        return None


class PluginConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    class_name = db.Column(db.String)
    enabled = db.Column(db.Boolean, default=True)
    name = db.Column(db.String)


class JournalEntryView(ModelView):
    column_list = (
        'owner',
        'create_date',
        'contents',
    )

    def summary(view, context, model, name):
        s = model.contents
        return s[:30] + (len(s) > 30) * '...'

    column_formatters = {
        'contents': summary,
    }


# ========== Setup Flask-Security ==========
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

if config.DEBUG_ENABLED:
    admin.add_view(
        JournalEntryView(
            JournalEntry, db.session, endpoint='model_view_journalentry'))
    admin.add_view(
        ModelView(
            PluginConfig, db.session, endpoint='model_view_pluginconfig'))
    admin.add_view(ModelView(User, db.session, endpoint='model_view_user'))


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


# ========== Marshmallow Schemas ==========

class UserSchema(marshmallow.ModelSchema):
    class Meta:
        model = User
        fields = ('id', 'username', 'email',)


class JournalEntrySchema(marshmallow.ModelSchema):
    class Meta:
        model = JournalEntry
        fields = ('id', 'contents', 'create_date', 'url', 'date_human', 'date_string', 'html')

    url = marshmallow.Method('get_url')

    def get_url(self, entry):
        return link_for_entry(entry)


user_schema = UserSchema()
journal_entry_schema = JournalEntrySchema()

from webapp.app_init import app, db, admin
import webapp.app_init
from webapp import config
from webapp import forms
from flask_admin.contrib.sqla import ModelView
import datetime
from webapp import parsing
import logging
import flask_migrate
import alembic
logger = logging.getLogger(__name__)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, index=True)
    password = db.Column(db.String(200))
    email = db.Column(db.String(200), unique=True, index=True)
    registered_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))

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
        return self.query_all_entries().order_by(
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

    def get_entries_tree(self, target_date=None) -> dict:
        """Return a tree structure of all entries belonging to this user.
        tree[year][month] = [day,day,day]"""
        query = self.query_all_entries().order_by(JournalEntry.create_date)
        if target_date is not None:
            query = self.query_all_entries().order_by(
                JournalEntry.create_date).filter(
                    JournalEntry.create_date >= target_date)

        query = query.order_by(JournalEntry.create_date.desc())

        entries_tree = dict()
        for e in query:
            if target_date is not None:
                if e.create_date.year > target_date.year:
                    break
            y = e.create_date.year
            m = e.create_date.month
            if y not in entries_tree:
                entries_tree[y] = dict()
            if m not in entries_tree[y]:
                entries_tree[y][m] = list()
            entries_tree[y][m].append(e)
        return entries_tree

    def get_settings_form(self) -> forms.AccountSetingsForm:
        """return a pre-filled form for changing user data"""
        form = forms.AccountSetingsForm()
        form.email.data = self.email
        form.first_name.data = self.first_name
        form.last_name.data = self.last_name
        return form

    def update_settings(self, settings_form: forms.AccountSetingsForm):
        """Takes a form and updates values from it."""
        form = settings_form
        if form.validate_on_submit():
            self.first_name = form.first_name.data
            self.last_name = form.last_name.data
            self.email = form.email.data
            if form.new_password.data == form.new_password_confirm.data:
                if form.password.data == self.password:
                    self.password = form.new_password.data
            db.session.add(self)
            db.session.commit()


class JournalEntry(db.Model):
    """Model for journal entries."""
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, index=True)
    contents = db.Column(db.String)
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id))
    owner = db.relationship(User, backref='users')

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

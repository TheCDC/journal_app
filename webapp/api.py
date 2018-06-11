from webapp import models
from webapp.extensions import app, marshmallow
import flask
import logging
import datetime
from sqlalchemy import inspect



logger = logging.getLogger(__name__)


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}



def link_for_date(**kwargs):
    """Return the app's link for the given date.
    The date is given as keyword arguments (year, month,day)."""
    expected = ['year', 'month', 'day']
    d = {k: kwargs[k] for k in expected if k in kwargs}
    with app.app_context():
        return flask.url_for('entry', **d)


def link_for_entry(entry: models.JournalEntry):
    """Return the app's link for the given journal entry.
    This function is a shortcut for link_for_date."""
    return link_for_date(
        year=entry.create_date.year,
        month=entry.create_date.month,
        day=entry.create_date.day)


def strip_datetime(d: datetime.datetime):
    return datetime.date(d.year, d.month, d.day)


def entry_exists(target_date: datetime.datetime):
    return models.JournalEntry.query.filter_by(
        create_date=strip_datetime(target_date)).first()


def get_entries_tree(target_user, target_date=None) -> dict:
    """Return a tree structure of all entries belonging to this user.
    tree[year][month] = [day,day,day]"""
    query = target_user.query_all_entries().order_by(models.JournalEntry.create_date)
    if target_date is not None:
        query = target_user.query_all_entries().order_by(
            models.JournalEntry.create_date).filter(
            models.JournalEntry.create_date >= target_date)

    query = query.order_by(models.JournalEntry.create_date.desc())

    entries_tree = dict()
    for e in query:
        if target_date is not None:
            if e.create_date.year > target_date.year:
                break
        y = e.create_date.year
        m = e.create_date.month
        if y not in entries_tree:
            entries_tree[y] = dict(months=dict(), num_entries=0)
        if m not in entries_tree[y]['months']:
            entries_tree[y]['months'][m] = list()
        entries_tree[y]['months'][m].append(e)
        entries_tree[y]['num_entries'] += 1
    return entries_tree


# ========== Marshmallow Schemas ==========
class UserSchema(marshmallow.ModelSchema):
    class Meta:
        model = models.User
        fields = ('id', 'username', 'email',)


class JournalEntrySchema(marshmallow.ModelSchema):
    class Meta:
        model = models.JournalEntry
        fields = ('id', 'contents', 'create_date', 'url', 'date_human', 'date_string', 'html')

    owner = marshmallow.Nested(UserSchema)
    url = marshmallow.Method('get_url')

    def get_url(self, entry):
        return link_for_entry(entry)


user_schema = UserSchema()
journal_entry_schema = JournalEntrySchema()



# make functions available in templates
app.jinja_env.globals.update(link_for_entry=link_for_entry, )

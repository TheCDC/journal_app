from webapp import models
from webapp.app_init import app, db
import datetime
import flask
import logging
import datetime
logger = logging.getLogger(__name__)


def link_for_date(**kwargs):
    """Return the app's link for the given date.
    The date is given as keyuword arguments (year, month,day)."""
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
    return datetime.datetime(d.year, d.month, d.day)


def entry_exists(target_date: datetime.datetime):
    return models.JournalEntry.query.filter_by(
        create_date=strip_datetime(target_date)).first()

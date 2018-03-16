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


def get_latest_entry() -> models.JournalEntry:
    """Return the chronologically latest JournalEntry."""
    return db.session.query(models.JournalEntry).order_by(
        models.JournalEntry.create_date.desc()).first()


def get_all_years() -> 'iterable[datetime.datetime]':
    """Return a list of dates corresponding to the range of
    years encompassed by all journal entries."""
    # define earliest and latest years of entries
    start_year = db.session.query(models.JournalEntry).order_by(
        models.JournalEntry.create_date).first()
    end_year = db.session.query(models.JournalEntry).order_by(
        models.JournalEntry.create_date.desc()).first()
    if start_year and end_year:
        for y in range(start_year.create_date.year,
                       end_year.create_date.year + 1):
            # find any entry within this year but before next year
            found = db.session.query(models.JournalEntry).filter(
                models.JournalEntry.create_date >= datetime.datetime(
                    y, 1, 1, 0, 0)).filter(
                        models.JournalEntry.create_date < datetime.datetime(
                            y + 1, 1, 1, 0, 0)).first()
            # only yield this year if has an entry
            if found:
                yield datetime.datetime(y, 1, 1, 0, 0)


def next_entry(e: models.JournalEntry) -> models.JournalEntry:
    """Return the first JournalEntry that falls chronologically after
    the given entry."""
    return db.session.query(models.JournalEntry).filter(
        models.JournalEntry.create_date > e.create_date).first()


def previous_entry(e: models.JournalEntry) -> models.JournalEntry:
    """Return the first JournalEntry that falls chronologically before
    the given entry."""
    return db.session.query(models.JournalEntry).filter(
        models.JournalEntry.create_date < e.create_date).order_by(
            models.JournalEntry.create_date.desc()).first()


def get_entries_tree(target_date=None) -> dict:
    query = db.session.query(models.JournalEntry).order_by(
        models.JournalEntry.create_date)
    if target_date is not None:
        query = db.session.query(models.JournalEntry).order_by(
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
            entries_tree[y] = dict()
        if m not in entries_tree[y]:
            entries_tree[y][m] = list()
        entries_tree[y][m].append(e)
    return entries_tree


def strip_datetime(d: datetime.datetime):
    return datetime.datetime(d.year, d.month, d.day)


def entry_exists(target_date: datetime.datetime):
    return models.JournalEntry.query.filter_by(
        create_date=strip_datetime(target_date)).first()

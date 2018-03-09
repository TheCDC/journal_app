from webapp import models
from webapp.app_init import app, db
import datetime
import flask


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

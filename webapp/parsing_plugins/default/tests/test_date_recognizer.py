from .. import date_recognizer
from webapp.models import JournalEntry
import datetime
from webapp.app_init import app


def test_parse():
    dates = ['2001-1-1', '2001-1-2', '2012-11-7']
    with app.app_context():
        e = JournalEntry(
            create_date=datetime.datetime.now(), contents=','.join(dates))
        parsed = list(date_recognizer.Plugin.parse_entry(e))
    for d, p in zip(dates, parsed):
        assert d in p
    assert len(parsed) == len(dates)

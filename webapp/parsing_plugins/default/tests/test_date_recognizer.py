from .. import date_recognizer
from webapp.models import JournalEntry
import datetime
from webapp.app_init import app

app.config['SERVER_NAME'] = 'localhost'


def test_parse():
    plugin_instance = date_recognizer.Plugin()
    dates = ['2001-1-1', '2001-1-2', '2012-11-7']
    with app.app_context():
        e = JournalEntry(
            create_date=datetime.datetime.now(), contents=', '.join(dates))
        parsed = list(plugin_instance.parse_entry(e))
        print(parsed)
    assert len(parsed) == len(dates)
    out_str =' '.join(parsed)
    for d in dates:
        assert d in out_str
    assert len(parsed) == len(dates)

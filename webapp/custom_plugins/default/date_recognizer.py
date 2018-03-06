from webapp import parsing
from webapp import models
import re

pattern = re.compile(r'[0-9]+-[0-9]+-[0-9]+')


class Plugin(parsing.Plugin):
    """Find dates mentioned in entries."""
    name = 'Date Recognizer'

    @classmethod
    def parse_entry(cls, e: models.JournalEntry):
        for f in pattern.findall(e.contents):
            yield f

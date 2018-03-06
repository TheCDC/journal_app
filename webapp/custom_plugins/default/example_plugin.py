from webapp import parsing
from webapp import models

import re

pattern = re.compile(r'[a-zA-Z]+')


class Plugin(parsing.Plugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Name Extractor'

    @classmethod
    def parse_entry(cls, e: models.JournalEntry):
        for w in pattern.findall(e.contents):
            try:
                if w[0].isalpha() and w[0] == w[0].upper():
                    yield w
            except IndexError:
                pass

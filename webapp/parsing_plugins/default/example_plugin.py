"""This module is an example of making a plugin.

It identifies capitalized words in the text of journal entries."""
from webapp import parsing
from webapp import models

import re

pattern = re.compile(r'\b[^\W\d_]+\b')


class Plugin(parsing.Plugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Name Extractor'

    @classmethod
    def parse_entry(cls, e: models.JournalEntry) -> 'iterable[str]':
        for w in pattern.findall(e.contents):
            try:
                if w[0].isalpha() and w[0] == w[0].upper():
                    yield w
            except IndexError:
                pass

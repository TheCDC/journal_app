"""This module is an example of making a plugin.

It identifies capitalized words in the text of journal entries."""
from webapp import parsing
from webapp import models

import re

pattern = re.compile(r'\b[^\W\d_]+\b')


class Plugin(parsing.Plugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Word Counter'

    @classmethod
    def parse_entry(cls, e: models.JournalEntry) -> 'iterable[str]':
        yield 'Number of words: {}'.format(len(pattern.findall(e.contents)))

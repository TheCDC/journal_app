"""This module is an example of making a plugin.

It identifies capitalized words in the text of journal entries."""
from webapp import parsing
from webapp import models

from collections import Counter

import re

pattern = re.compile(r'\b[^\W\d_]+\b')


class Plugin(parsing.Plugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Word Stats'

    @classmethod
    def parse_entry(cls, e: models.JournalEntry) -> 'iterable[str]':
        words = list(pattern.findall(e.contents.lower()))
        yield 'Word count: <span class="pull-right"> {} </span>'.format(
            len(words))
        yield 'Unique words: <span class="pull-right"> {} </span>'.format(
            len(set(words)))
        for t in Counter(words).most_common():
            yield '{}: <span class="pull-right">{}</span>'.format(*t)

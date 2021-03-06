from collections import Counter
from webapp.journal_plugins.validation import validate
from webapp.journal_plugins import classes
from webapp import models
import re
from . import views

pattern = re.compile(r'\b[^\W\d_]+\b')


class Plugin(classes.BasePlugin):
    """Counts the number of words and unique words in an entry."""
    name = 'Word Counter'
    description = 'Count total words as well as number of unique words used in an entry.'
    cache_schema_version = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager.blueprint.add_url_rule(self.endpoint,
                                            view_func=views.IndexView.as_view(f'{self.url_rule_base_name}-index'))

    def _parse_entry(self, e: 'models.JournalEntry'):
        words = list(pattern.findall(e.contents.lower()))
        unique_words = set(words)
        num_words = len(words)
        num_unique_words = len(unique_words)
        obj = dict(num_words=num_words, num_unique_words=num_unique_words, unique_ratio=num_unique_words / num_words,
                   entry=models.journal_entry_schema.dump(obj=e))
        return obj

    @validate
    def parse_entry(self, e: 'models.JournalEntry') -> 'iterable[str]':
        obj = self._parse_entry(e)
        yield dict(html='Word count: {} '.format(
            obj['num_words']))
        yield dict(html='Unique words: {} '.format(
            obj['num_unique_words']))
        yield dict(html='Unique Ratio: {:.3f} '.format(
            obj['unique_ratio']))


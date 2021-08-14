from collections import Counter
from webapp.journal_plugins import classes
from webapp import models
import re
from . import views
pattern = re.compile(r'\b[^\W\d_]+\b')


class Plugin(classes.BasePlugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Word Counter'
    description = 'Count total words as well as number of unique words used in an entry.'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager.blueprint.add_url_rule(self.endpoint, view_func=views.IndexView.as_view(f'{self.url_rule_base_name}-index'))

    def parse_entry(self, e: 'models.JournalEntry') -> 'iterable[str]':
        words = list(pattern.findall(e.contents.lower()))
        yield 'Word count: <span class="pull-right"> {} </span>'.format(
            len(words))
        yield 'Unique words: <span class="pull-right"> {} </span>'.format(
            len(set(words)))

"""This module is an example of making a plugin.

It identifies capitalized words in the text of journal entries."""
from webapp import models
from webapp.journal_plugins import classes
from . import views
import flask
import re
import flask_login
pattern = re.compile(r'\b[^\W\d_]+\b')

# pattern = re.compile("/^[a-z ,.'-]+$/i")
def count_occurrences(search):
    all_entries = models.JournalEntry.query.filter(models.JournalEntry.owner_id == flask_login.current_user.id)
    return all_entries.filter(
                models.JournalEntry.contents.contains(search)).count()



class Plugin(classes.BasePlugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Name Search'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager.blueprint.add_url_rule(self.endpoint, view_func=views.NameExtractorPluginView.as_view(f'{self.url_rule_base_name}.index'))


    def parse_entry(self, e: models.JournalEntry) -> 'iterable[str]':
        seen = set()
        words = list(pattern.findall(e.contents))
        out = []
        for w in words:
            try:
                if w[0].isalpha() and w[0] == w[0].upper():
                    if w not in seen:
                        c = count_occurrences(w)
                        label = f'{w} ({c}),'
                        url = flask.url_for(f'site.plugins.{self.safe_name}.index' , page=1, search=w)
                        out.append(
                            f'<a href="{url}" >{label}</a>'
                        )
                    seen.add(w)
            except IndexError:
                pass
        yield 'Names found: {}'.format(len(out))
        yield from out

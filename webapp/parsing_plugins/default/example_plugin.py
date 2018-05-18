"""This module is an example of making a plugin.

It identifies capitalized words in the text of journal entries."""
from webapp import parsing
from webapp import models
import re
import flask_login
from flask.views import MethodView
pattern = re.compile(r'\b[^\W\d_]+\b')

class NameRecognizerPluginView(MethodView):
    def get(self,**kwargs):
        return 'Hello this is Name Recognizer'

class Plugin(parsing.Plugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Name Extractor'
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self._view = NameRecognizerPluginView

    def parse_entry(self, e: models.JournalEntry) -> 'iterable[str]':
        seen = set()
        words = list(pattern.findall(e.contents))
        out = []
        for w in words:
            try:
                if w[0].isalpha() and w[0] == w[0].upper():
                    if w not in seen:
                        out.append(w)
                    seen.add(w)
            except IndexError:
                pass
        yield 'Names found: {}'.format(len(out))
        yield from out

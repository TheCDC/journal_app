"""This module is an example of making a plugin.

It identifies capitalized words in the text of journal entries."""
import webapp.models
from webapp.journal_plugins import classes
from webapp.extensions import db
from webapp import app
from . import views
from . import models

from flask_sqlalchemy import SQLAlchemy
import flask
import re
import flask_login
import json

# create new db connection to avoid ruining the main db connection
db = SQLAlchemy(app)

pattern = re.compile(r'\b[^\W\d_]+\b')


# pattern = re.compile("/^[a-z ,.'-]+$/i")
def count_occurrences(search):
    all_entries = webapp.models.JournalEntry.query.filter(
        webapp.models.JournalEntry.owner_id == flask_login.current_user.id)
    return all_entries.filter(
        webapp.models.JournalEntry.contents.contains(search)).count()


class Plugin(classes.BasePlugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Name Search'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager.blueprint.add_url_rule(self.endpoint, view_func=views.NameExtractorPluginView.as_view(
            f'{self.url_rule_base_name}-index'))
        # _ = models.NameSearchCache.query.first()

    def _parse_entry(self, e):
        seen = set()
        words = list(pattern.findall(e.contents))
        out = []
        for w in words:
            try:
                if w[0].isalpha() and w[0] == w[0].upper():
                    if w not in seen:
                        c = count_occurrences(w)
                        label = f'{w} ({c}),'
                        url = flask.url_for(f'site.plugins-{self.safe_name}-index', page=1, search=w)
                        out.append(
                            f'<a href="{url}" >{label}</a>'
                        )
                    seen.add(w)
            except IndexError:
                pass
        yield 'Names found: {}'.format(len(out))
        yield from out

    def parse_entry(self, e: 'webapp.models.JournalEntry') -> 'iterable[str]':
        session = db.session.object_session(e)

        results = list(self._parse_entry(e))

        found = models.NameSearchCache.query.filter(models.NameSearchCache.parent == e).first()
        if found:
            if (found.updated_at < e.create_date):

                results = list(self._parse_entry(e))
                found.json = json.dumps(results)
                session.add(found)
                session.commit()

            else:
                results = json.loads(found.json)
            session.close()

            return results
        else:

            results = list(self._parse_entry(e))
            found = models.NameSearchCache(parent=e, json=json.dumps(results))
            session.add(found.parent)
            session.add(found)
            session.commit()
            return results
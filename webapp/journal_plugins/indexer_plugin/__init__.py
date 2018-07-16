"""This module is an example of making a plugin.

It identifies capitalized words in the text of journal entries."""
from typing import List
import webapp.models
from webapp.journal_plugins import classes
from webapp.journal_plugins.validation import validate

from webapp.extensions import db
from webapp import app
from . import views
from . import models

from flask_sqlalchemy import SQLAlchemy
import re
import json
from nltk.corpus import stopwords

all_stopwords = stopwords.words('english')

# create new db connection to avoid ruining the main db connection
db = SQLAlchemy(app)

pattern = re.compile(r'^#+.+',flags=re.MULTILINE)


def extract_headings(entry):
    return list(i.strip() for i in pattern.findall(entry.contents))


class Plugin(classes.BasePlugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Headings Indexer'
    description = """Identify headings you use in your entries. Headings are any number of octothorpes, #, followed by any text.
    Use them to organize your thoughts. This plugin will create a summary index for you to browse."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager.blueprint.add_url_rule(self.endpoint, view_func=views.IndexerPluginView.as_view(
            f'{self.url_rule_base_name}-index'))
        # _ = models.NameSearchCache.query.first()

    def _parse_entry(self, e, session=None):
        if session is None:
            session = db.session.object_session(e)
        if session is None:
            session = db.session()
        session.add(e)
        out = []
        for h in extract_headings(e):
            item = dict(html=h,label=h)
            yield item

    @validate
    def parse_entry(self, e: 'webapp.models.JournalEntry') -> 'List[str]':
        session = db.session

        found = session.query(models.IndexerPluginCache).filter(models.IndexerPluginCache.parent == e).first()

        if found:
            if (found.updated_at < e.updated_at):

                results = list(self._parse_entry(e))
                found.json = json.dumps(results)
                session.add(found)
                session.commit()

            else:
                results = json.loads(found.json)
            try:
                return classes.PluginReturnValue(results).dict
            except ValueError:
                session.delete(found)
                session.commit()

        results = list(self._parse_entry(e))
        found = models.IndexerPluginCache(parent=e, json=json.dumps(results))
        session = db.session.object_session(e)
        session.add(found)
        session.commit()
        return results

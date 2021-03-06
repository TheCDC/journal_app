"""This module is an example of making a plugin.

It identifies capitalized words in the text of journal entries."""
import webapp.models
from webapp.journal_plugins import classes, models
from webapp.journal_plugins.validation import validate

from webapp.extensions import db
from webapp import app
from . import views

from flask_sqlalchemy import SQLAlchemy
import flask
import re
import flask_login
import json
from nltk.corpus import stopwords

all_stopwords = stopwords.words('english')

# create new db connection to avoid ruining the main db connection
db = SQLAlchemy(app)

pattern = re.compile(r'\b[^\W\d_]+\b')


# pattern = re.compile("/^[a-z ,.'-]+$/i")
def count_occurrences(user, search):
    all_entries = webapp.models.JournalEntry.query.filter(
        webapp.models.JournalEntry.owner_id == user.id)
    return all_entries.filter(
        webapp.models.JournalEntry.contents.contains(search)).count()


class Plugin(classes.BasePlugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Name Search'
    description = "Identify names you mention in your entries and find other entries with those names."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager.blueprint.add_url_rule(self.endpoint, view_func=views.NameExtractorPluginView.as_view(
            f'{self.url_rule_base_name}-index'))
        # _ = models.NameSearchCache.query.first()

    @validate
    def parse_entry(self, e, session=None):
        if session is None:
            session = db.session.object_session(e)
        if session is None:
            session = db.session()
        session.add(e)
        seen = set()
        words = list(w for w in pattern.findall(e.contents) if w.lower() not in all_stopwords)
        out = []
        for w in words:
            try:
                if w[0] == w[0].upper():
                    if w not in seen:
                        c = count_occurrences(
                            webapp.models.User.query.filter(webapp.models.User.id == e.owner_id).first(), w)
                        label = f'{w}'
                        url = flask.url_for(f'site.plugins-{self.safe_name}-index', page=1, search=w)
                        out.append(
                            dict(
                                html=f'<a href="{url}" >{label}</a>',
                                url=url,
                                label=label,
                            )
                        )
                    seen.add(w)
            except IndexError:
                pass

        yield from out


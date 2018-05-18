"""This module is an example of making a plugin.

It identifies capitalized words in the text of journal entries."""
from webapp import parsing
from webapp import models
from webapp import api
import re
import flask_login
from flask.views import MethodView
from flask import request
import flask

pattern = re.compile(r'\b[^\W\d_]+\b')


class NameExtractorPluginView(MethodView):
    def get_context(self, request):
        data = request.args
        context = dict()
        context['page'] = int(data.get('page', 0))
        context['search'] = data.get('search', [])
        return context

    def get_objects(self, context):
        all_entries = models.JournalEntry.query.filter(models.JournalEntry.owner_id == flask_login.current_user.id)
        filtered_by_search = all_entries.filter(
            models.JournalEntry.contents.contains(context['search']))
        # Flask-SQLalchemy pagination docs
        # http://flask-sqlalchemy.pocoo.org/2.1/api/?highlight=pagination#flask.ext.sqlalchemy.Pagination
        return filtered_by_search.paginate(
            context['page'], 10,
            False)

    def get(self, **kwargs):
        name = flask_login.current_user.first_name
        context = self.get_context(request)
        pagination = self.get_objects(context)
        context['pagination'] = pagination
        context['pagination_annotated'] = [dict(item=item,link=api.link_for_entry(item)) for item in pagination.items]
        try:
            return flask.render_template('plugins/name_extractor.html', context=context)
            # return 'Name Recognizer {pagination.items[0].contents} {pagination.items}'.format(pagination=context['pagination'])
        except IndexError:
            flask.abort(400)


class Plugin(parsing.Plugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Name Extractor'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._view = NameExtractorPluginView

    def parse_entry(self, e: models.JournalEntry) -> 'iterable[str]':
        seen = set()
        words = list(pattern.findall(e.contents))
        out = []
        for w in words:
            try:
                if w[0].isalpha() and w[0] == w[0].upper():
                    if w not in seen:
                        url = flask.url_for('plugin.' + self.get_unique_name(), page=1, search=w)
                        out.append(
                            f'<a href="{url} ">{w}</a>'
                        )
                    seen.add(w)
            except IndexError:
                pass
        yield 'Names found: {}'.format(len(out))
        yield from out

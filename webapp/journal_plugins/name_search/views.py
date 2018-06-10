from webapp import models

from webapp import api


import flask_login
from flask.views import MethodView
from flask import request

import flask

from webapp.journal_plugins import extensions
class NameExtractorPluginView(MethodView):
    def get_context(self, request):
        data = request.args
        context = dict()
        context['page'] = int(data.get('page', 0))
        context['search'] = data.get('search', '')
        return context

    def get_objects(self, context):

        all_entries = models.JournalEntry.query.filter(models.JournalEntry.owner_id == flask_login.current_user.id)
        if len(context['search']) > 0:
            filtered_by_search = all_entries.filter(
                models.JournalEntry.contents.contains(context['search']))
        else:
            filtered_by_search = all_entries.filter(
                models.JournalEntry.contents.contains(''))
        # Flask-SQLalchemy pagination docs
        # http://flask-sqlalchemy.pocoo.org/2.1/api/?highlight=pagination#flask.ext.sqlalchemy.Pagination
        return filtered_by_search.order_by(models.JournalEntry.create_date).paginate(
            context['page'], 10,
            False)

    def get(self, **kwargs):
        name = flask_login.current_user.first_name
        context = self.get_context(request)

        pagination = self.get_objects(context)
        context['pagination'] = pagination
        context['pagination_annotated'] = [dict(item=item, link=api.link_for_entry(item)) for item in pagination.items]
        try:
            return flask.render_template(f'{extensions.name_search.safe_name}/name_extractor.html', context=context)
            # return 'Name Recognizer {pagination.items[0].contents} {pagination.items}'.format(pagination=context['pagination'])
        except IndexError:
            flask.abort(400)

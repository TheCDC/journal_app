import flask
import flask_login
from flask.views import MethodView
from flask import request

from webapp import models
from webapp import api
from webapp.journal_plugins import extensions
from collections import Counter

class NameExtractorPluginView(MethodView):
    def foo(self, context):
        objects = [
            dict(entry=models.journal_entry_schema.dump(obj=e).data,
                 output=extensions.name_search.parse_entry(e))
            for e in self.get_objects(context).items]
        context['summary_objects'] = objects
        seen_cards = list()
        for i in objects:
            for card in i['output']:
                try:
                    seen_cards.append(card['label'])
                except TypeError:
                    seen_cards.append(card)


        ctr = Counter(seen_cards)
        most_common = list(ctr.most_common())
        context['summary'] = dict(most_common=most_common, objects=objects)

    def get_context(self, request):
        data = request.args
        context = dict(plugin=extensions.name_search.to_dict())
        context['page'] = int(data.get('page', 0))
        context['search'] = data.get('search', '')
        if 'search' in data:


            pagination = self.get_objects(context)
            context['pagination'] = pagination
            context['pagination_annotated'] = [dict(item=item, link=api.link_for_entry(item)) for item in
                                               pagination.items]
        else:
            args = flask.request.args
            self.foo(context)

        return context

    def get_objects(self, context):

        all_entries = models.JournalEntry.query.filter(models.JournalEntry.owner_id == flask_login.current_user.id)
        if len(context['search']) > 0:
            filtered_by_search = all_entries.filter(
                models.JournalEntry.contents.contains(context['search'])).order_by(models.JournalEntry.create_date)
        else:
            filtered_by_search = all_entries.order_by(models.JournalEntry.create_date.desc())
        # Flask-SQLalchemy pagination docs
        # http://flask-sqlalchemy.pocoo.org/2.1/api/?highlight=pagination#flask.ext.sqlalchemy.Pagination
        return filtered_by_search.order_by(models.JournalEntry.create_date).paginate(
            context['page'], 10,
            False)

    @flask_login.login_required
    def get(self, **kwargs):
        name = flask_login.current_user.first_name
        context = self.get_context(request)

        try:
            return flask.render_template(f'{extensions.name_search.safe_name}/index.html', context=context)
            # return 'Name Recognizer {pagination.items[0].contents} {pagination.items}'.format(pagination=context['pagination'])
        except IndexError:
            flask.abort(400)

import flask
import flask_login
from flask.views import MethodView
from flask import request

from webapp import models
from webapp import api
from webapp.journal_plugins import extensions
from collections import Counter
import datetime


class IndexerPluginView(MethodView):
    def get_summary(self, context):
        objects = [
            dict(entry=models.journal_entry_schema.dump(obj=e).data,
                 output=extensions.name_search.parse_entry(e))
            for e in self.get_objects(context).items]
        context['summary_objects'] = objects
        seen_names = list()
        for i in objects:
            for name in i['output']:
                try:
                    seen_names.append(name['label'])
                except TypeError:
                    seen_names.append(name)

        ctr = Counter(seen_names)
        most_common = list(ctr.most_common())
        context['summary'] = dict(most_common=most_common, objects=objects)

    def get_context(self, request):
        data = request.args
        plugin = extensions.name_search
        pdict = plugin.to_dict()
        context = dict(plugin=pdict, plugin_and_preference=dict(plugin=pdict,
                                                                preference=plugin.get_preference_model(
                                                                    flask_login.current_user)))
        context['page'] = int(data.get('page', 0))
        context['search'] = data.get('search', '')
        if 'search' in data:
            pagination = self.get_objects(context)
            context['pagination'] = pagination
            context['pagination_annotated'] = [dict(item=item, link=api.link_for_entry(item)) for item in
                                               pagination.items]
        else:
            args = flask.request.args
            self.get_summary(context)

        return context

    def get_objects(self, context):

        all_entries = models.JournalEntry.query.filter(models.JournalEntry.owner_id == flask_login.current_user.id)
        if len(context['search']) > 0:
            filtered_by_search = all_entries.filter(
                models.JournalEntry.contents.contains(context['search'])).order_by(
                models.JournalEntry.create_date.desc())
            return filtered_by_search.paginate(context['page'], 10, False)

        else:
            now = datetime.datetime.now().date()
            then = now - datetime.timedelta(days=30)
            filtered_by_search = all_entries.order_by(models.JournalEntry.create_date)
            return filtered_by_search.filter(models.JournalEntry.create_date >= then).paginate(context['page'], 30,
                                                                                               False)

        # Flask-SQLalchemy pagination docs
        # http://flask-sqlalchemy.pocoo.org/2.1/api/?highlight=pagination#flask.ext.sqlalchemy.Pagination

    @flask_login.login_required
    def get(self, **kwargs):
        name = flask_login.current_user.first_name
        context = self.get_context(request)

        try:
            return flask.render_template(f'{extensions.name_search.safe_name}/index.html', context=context)
            # return 'Name Recognizer {pagination.items[0].contents} {pagination.items}'.format(pagination=context['pagination'])
        except IndexError:
            flask.abort(400)

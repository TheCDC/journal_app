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
                 output=list(extensions.indexer_plugin._parse_entry_cached(e)))
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
        context = dict(args=data)

        context['latest_date'] = models.JournalEntry.query.filter(
            models.JournalEntry.owner_id == flask_login.current_user.id).order_by(
            models.JournalEntry.create_date.desc()).first().date_string

        end_date = data.get('end', context['latest_date'])
        context['end'] = end_date
        self.get_summary(context)

        return context

    def get_objects(self, context):
        now = datetime.date(*map(int,context['end'].split('-')))
        print('now',now)

        owned_entries = models.JournalEntry.query.filter(models.JournalEntry.owner_id == flask_login.current_user.id)

        then = now - datetime.timedelta(days=30)
        print('then',then)
        ordered_entries = owned_entries.order_by(models.JournalEntry.create_date.desc())
        pagination = ordered_entries.filter(models.JournalEntry.create_date <= now).paginate(0, 30,
                                                                                      False)
        print(pagination.items)
        return pagination

        # Flask-SQLalchemy pagination docs
        # http://flask-sqlalchemy.pocoo.org/2.1/api/?highlight=pagination#flask.ext.sqlalchemy.Pagination

    @flask_login.login_required
    def get(self, **kwargs):
        if 'end'not in request.args:
            return flask.redirect(flask.url_for('site.plugins-headings_indexer-index', end=models.JournalEntry.query.filter(
            models.JournalEntry.owner_id == flask_login.current_user.id).order_by(
            models.JournalEntry.create_date.desc()).first().date_string))

        name = flask_login.current_user.first_name
        context = self.get_context(request)


        try:
            return flask.render_template(f'indexer/index.html', context=context)
            # return 'Name Recognizer {pagination.items[0].contents} {pagination.items}'.format(pagination=context['pagination'])
        except IndexError:
            flask.abort(400)

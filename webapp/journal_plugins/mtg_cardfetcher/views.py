from . import models as mymodels
from webapp import models
from webapp.journal_plugins import extensions
from flask.views import MethodView
import flask
import flask_login


class IndexView(MethodView):
    def get_objects(self, context):
        q = models.JournalEntry.query.filter(models.JournalEntry.owner == flask_login.current_user).order_by(
            models.JournalEntry.create_date.desc())[:30]
        return q

    def get_context(self, **kwargs):
        args = flask.request.args
        context = dict(plugin=extensions.mtg_cardfetcher.to_dict())
        objects = [dict(entry=models.journal_entry_schema.dump(obj=e).data, output=extensions.mtg_cardfetcher.parse_entry(e)) for e in self.get_objects(context)]
        context['objects'] = objects

        return context

    def get(self, **kwargs):
        return flask.render_template(f'mtg_cardfetcher/index.html', context=self.get_context(**kwargs))

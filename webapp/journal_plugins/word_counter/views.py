from flask.views import MethodView
import flask
from webapp import models
from webapp.journal_plugins import extensions
import flask_login


class IndexView(MethodView):
    def get_objects(self, context):
        q = models.JournalEntry.query.filter(models.JournalEntry.owner == flask_login.current_user).order_by(
            models.JournalEntry.create_date.desc())[:30]
        return q

    def get_context(self, **kwargs):
        context = dict(plugin=extensions.word_counter.to_dict())
        objs = [dict(entry=models.journal_entry_schema.dump(obj=e).data, output=list(extensions.word_counter.parse_entry(e))) for e in self.get_objects(context)]
        context['objects'] = objs
        return context

    def get(self, **kwargs):
        return flask.render_template('word_counter/index.html', context=self.get_context(**kwargs))

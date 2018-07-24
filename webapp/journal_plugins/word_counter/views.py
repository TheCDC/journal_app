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
        objs = []
        for e in self.get_objects(context):
            # cache results
            extensions.word_counter.parse_entry(e)
            # processed results html
            objs.append(extensions.word_counter._parse_entry(e))
        context['objects'] = objs
        word_sum = 0
        num_unique_words = 0
        for d in objs:
            word_sum += d['num_words']
            num_unique_words += d['num_unique_words']

        summary_obj = dict(num_words=word_sum, num_unique_words=num_unique_words)
        context['summary'] = summary_obj

        plugin = extensions.word_counter
        pdict = plugin.to_dict()
        context.update(dict(
            plugin=pdict, plugin_and_preference=dict(
                plugin=pdict,
                preference=plugin.get_preference_model(
                    flask_login.current_user))
        ))
        return context

    @flask_login.login_required
    def get(self, **kwargs):
        return flask.render_template('word_counter/index.html', context=self.get_context(**kwargs))

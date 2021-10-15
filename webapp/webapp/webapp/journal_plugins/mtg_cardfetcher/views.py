from webapp import models
from webapp.journal_plugins import extensions
from flask.views import MethodView
import flask
import flask_login
from collections import Counter


class IndexView(MethodView):
    def get_objects(self, context):
        q = models.JournalEntry.query.filter(models.JournalEntry.owner == flask_login.current_user).order_by(
            models.JournalEntry.create_date.desc())[:30]
        return q

    def get_context(self, **kwargs):
        args = flask.request.args
        context = dict(plugin=extensions.mtg_cardfetcher.to_dict())
        objects = [
            dict(entry=models.journal_entry_schema.dump(obj=e).data,
                 output=list(extensions.mtg_cardfetcher._parse_entry_cached(e)))
            for e in self.get_objects(context)]
        context['objects'] = objects
        seen_cards = list()
        for i in objects:
            for card in i['output']:
                seen_cards.append(card['html'])
        ctr = Counter(c for c in seen_cards)
        summary = list(ctr.most_common())
        context['summary'] = summary
        plugin = extensions.mtg_cardfetcher
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
        return flask.render_template(f'mtg_cardfetcher/index.html', context=self.get_context(**kwargs))

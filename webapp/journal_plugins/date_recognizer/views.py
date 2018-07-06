from flask.views import MethodView
import flask
from . import models
from webapp.journal_plugins import extensions
import flask_login


class IndexView(MethodView):

    def get_context(self, **kwargs):
        context = dict(plugin=extensions.date_recognizer.to_dict())
        plugin = extensions.date_recognizer
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
        return flask.render_template('date_recognizer/index.html', context=self.get_context(**kwargs))

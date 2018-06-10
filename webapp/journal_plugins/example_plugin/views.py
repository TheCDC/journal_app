from flask.views import MethodView
import flask
from . import models
from webapp.journal_plugins import extensions



class IndexView(MethodView):
    def get_context(self, **kwargs):
        context = dict(plugin=extensions.example_plugin.to_dict())
        return context

    def get(self, **kwargs):
        return flask.render_template('example_plugin/index.html', context=self.get_context(**kwargs))

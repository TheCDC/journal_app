from flask.views import MethodView
import flask
from . import models
from webapp.journal_plugins import extensions



class IndexView(MethodView):
    def get_context(self, **kwargs):
        return extensions.example_plugin.get_default_context()

    def get(self, **kwargs):
        return flask.render_template('example_plugin/index.html', context=self.get_context(**kwargs))

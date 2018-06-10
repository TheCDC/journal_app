from flask.views import MethodView
import flask
from .extensions import plugin_manager

class ExampleView(MethodView):
    def get(self,**kwargs):
        return flask.render_template('journal_plugins_index.html', context=kwargs)
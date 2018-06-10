from flask.views import MethodView
import flask
from .extensions import plugin_manager

class ExampleView(MethodView):
    def get_context(self,**kwargs):
        context = dict(plugins=list())
        for k,v in plugin_manager.plugins.items():
            context['plugins'].append(v.to_dict())
        return context

    def get(self,**kwargs):
        return flask.render_template('journal_plugins_index.html', context=self.get_context(**kwargs))
from flask import Blueprint
from . import views
import webapp
import logging

logger = logging.getLogger(__name__)


class PluginManager:
    def __init__(self):

        self.blueprint = Blueprint(
            'site',
            __name__,
            template_folder='templates',
            static_folder='static',
            url_prefix='/plugins'
        )

        self.url = '/'
        self.blueprint.add_url_rule(self.url, view_func=views.ExampleView.as_view('plugins.index'))

        self.plugins = dict()

    def register_plugin(self, plugin):
        if plugin.name in self.plugins:
            raise ValueError(f'Plugins must have unique names! Plugin "{plugin.name}" already registered!')
        else:
            self.plugins[plugin.name] = plugin
    def  init_app(self,app):
        app.register_blueprint(self.blueprint)




class BasePlugin:
    name = 'Default Plugin Name'

    def __init__(self, plugin_manager: PluginManager):
        self.name = self.__class__.name
        plugin_manager.register_plugin(self)
        self.manager = plugin_manager
        self.url = '/'+'/'.join([i for i in plugin_manager.url.split('/') if len(i) > 0] + [self.safe_name])
        self.url_rule_base_name = f'plugins.{self.safe_name}'

    def parse_entry(self, e):
        raise NotImplementedError()

    @property
    def safe_name(self):
        return self.__class__.name.lower().replace(' ', '_')



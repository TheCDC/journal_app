from flask import Blueprint
import os
from . import views
class PluginManager:
    def __init__(self,view_func=None):

        self.blueprint = Blueprint(
            'site',
            __name__,
            template_folder=os.path.join(os.path.dirname(__file__),'templates'),
            static_folder='static',
            url_prefix='/plugins'
        )

        self.url = '/'

        self.plugins = dict()

    def register_plugin(self, plugin):
        if plugin.name in self.plugins:
            raise ValueError(f'Plugins must have unique names! Plugin "{plugin.name}" already registered!')
        else:
            self.plugins[plugin.name] = plugin

    def init_app(self, app, view_func=None):
        if view_func:
            self.blueprint.add_url_rule(self.url, view_func=view_func)
        app.register_blueprint(self.blueprint)

    def parse_entry(self, e):
        for p in self.plugins.items():
            yield (p[1], p[1].parse_entry(e))


class BasePlugin:
    name = 'Default Plugin Name'

    def __init__(self, plugin_manager: PluginManager):
        self.name = self.__class__.name
        plugin_manager.register_plugin(self)
        self.manager = plugin_manager
        self.url = '/' + '/'.join([i for i in plugin_manager.url.split('/') if len(i) > 0] + [self.safe_name])
        self.url_rule_base_name = f'plugins.{self.safe_name}'

    def parse_entry(self, e):
        raise NotImplementedError()

    @property
    def safe_name(self):
        return self.__class__.name.lower().replace(' ', '_')

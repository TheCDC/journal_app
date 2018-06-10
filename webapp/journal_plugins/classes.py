from flask import Blueprint, url_for
import os
from . import views


def concat_urls(a, b):
    return '/' + '/'.join(x for x in (a.split('/') + b.split('/')) if len(x) > 0)


class PluginManager:
    def __init__(self, view_func=None):
        # the plugin manager creates a a parent endpoint for all the plugins
        self.blueprint = Blueprint(
            'site',
            __name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
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
        """Bootstrap the plugin manager onto the Flask app."""
        if view_func:
            self.blueprint.add_url_rule(self.url, view_func=view_func)
        app.register_blueprint(self.blueprint)

    def parse_entry(self, e):
        """Call all registered plugins on the entry."""
        for p in self.plugins.items():
            yield (p[1], p[1].parse_entry(e))


class BasePlugin:
    name = 'Default Plugin Name'

    def __init__(self, plugin_manager: PluginManager):
        self.name = self.__class__.name
        plugin_manager.register_plugin(self)
        self.manager = plugin_manager
        # create a url endpoint (just the endpoint) for this plugin based on its name
        self.url = concat_urls(self.manager.blueprint.url_prefix, self.safe_name)
        self.endpoint = f'/{self.safe_name}'

        self.url_rule_base_name = f'plugins.{self.safe_name}'

    def parse_entry(self, e):
        """The developer must override this in order to provide entry parsing functionality"""
        raise NotImplementedError()

    def get_default_context(self):
        return dict(name=self.name, url=self.url)

    @property
    def safe_name(self):
        """A URL self version of this plugin's name."""
        return self.__class__.name.lower().replace(' ', '_')

    def to_dict(self):
        """A JSON ready representation of this plugin."""
        return dict(name=self.name, url=self.url, safe_name=self.safe_name, type='journal_plugin')

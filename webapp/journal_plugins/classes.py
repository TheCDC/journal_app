from flask import Blueprint
import flask
import os
from webapp import config
import logging


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
            yield dict(plugin=p[1].to_dict(), output=p[1].parse_entry(e))


class BasePlugin:
    name = 'Default Plugin Name'
    description = 'Description for the BasePlugin'
    def __init__(self, plugin_manager: PluginManager):
        self.name = self.__class__.name
        self.description = self.__class__.description

        plugin_manager.register_plugin(self)
        self.manager = plugin_manager
        # create a url endpoint (just the endpoint) for this plugin based on its name
        self.url = concat_urls(self.manager.blueprint.url_prefix, self.safe_name)
        self.endpoint = f'/{self.safe_name}'

        self.url_rule_base_name = f'plugins-{self.safe_name}'
        self.resources_path = os.path.join(config.CONFIG_PATH, 'plugins', self.safe_name)
        try:
            os.makedirs(self.resources_path)
            logging.info('created plugin data directory: %s', self.resources_path)
        except FileExistsError:
            pass


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
        return dict(name=self.name, url=self.url, safe_name=self.safe_name, type='journal_plugin',description=self.description,back=flask.url_for('site.plugins-index'))

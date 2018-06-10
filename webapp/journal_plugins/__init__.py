from flask import Blueprint
from . import example_plugin
from . import views
from webapp import app



class PluginManager:
    def __init__(self, app):

        self.blueprint = Blueprint(
            'site',
            __name__,
            template_folder='templates',
            static_folder='static',
            url_prefix='/example_blueprint'
        )

        self.blueprint.add_url_rule('/', view_func=views.ExampleView.as_view('index'))

        app.register_blueprint(self.blueprint)
        self.plugins = dict()

    def register_plugin(self, plugin):
        if plugin.name in self.plugins:
            raise ValueError('Plugins must have unique names! Plugin "{plugin.name}" already registered!')
        else:
            self.plugins[plugin.name] = plugin

class BasePlugin:
    name = 'Default Plugin Name'
    def __init__(self, plugin_manager):
        self.name = self.__class__.name
        plugin_manager.register_plugin(self)

    def parse_entry(self, e):
        raise NotImplementedError()

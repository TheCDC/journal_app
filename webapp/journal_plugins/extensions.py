from webapp import app
# ==========  Journal Parsing Plugins - Instantiate manager==========
from .classes import PluginManager

plugin_manager = PluginManager()

# ==========  Journal Parsing Plugins - Register plugins==========

from . import example_plugin

example_plugin = example_plugin.Plugin(plugin_manager)

from . import date_recognizer

date_recognizer = date_recognizer.Plugin(plugin_manager)

plugin_manager.init_app(app)

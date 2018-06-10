from webapp import app
# ==========  Journal Parsing Plugins - Instantiate manager ==========
from .classes import PluginManager

plugin_manager = PluginManager()

# ==========  Journal Parsing Plugins - Register plugins ==========
# Example Plugin
from . import example_plugin

example_plugin = example_plugin.Plugin(plugin_manager)
# Date Recognizer
from . import date_recognizer

date_recognizer = date_recognizer.Plugin(plugin_manager)

# Name Search
from . import name_search

name_search = name_search.Plugin(plugin_manager)

# ==========  Journal Parsing Plugins - Apply plugins to app==========

plugin_manager.init_app(app)

print(app.url_map)

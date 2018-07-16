from webapp import app
from webapp.extensions import db
# ==========  Journal Parsing Plugins - Instantiate manager ==========
from .classes import PluginManager

plugin_manager = PluginManager()




# ==========  Journal Parsing Plugins - Register plugins ==========
# Date Recognizer
from . import date_recognizer

date_recognizer = date_recognizer.Plugin(plugin_manager)

# Name Search
from . import name_search

name_search = name_search.Plugin(plugin_manager)

# Word Counter
from . import word_counter

word_counter = word_counter.Plugin(plugin_manager)

# MTG Cardfetcher
from . import mtg_cardfetcher

mtg_cardfetcher = mtg_cardfetcher.Plugin(plugin_manager)


# Headings Indexer
from . import indexer_plugin

indexer_plugin = indexer_plugin.Plugin(plugin_manager)

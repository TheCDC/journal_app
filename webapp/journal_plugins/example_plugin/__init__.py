import webapp.journal_plugins
from webapp import db


class Plugin(webapp.journal_plugins.BasePlugin):
    name = 'Example Plugin'
    def parse_entry(self, e):
        yield 'This is the output of the example plugin.'
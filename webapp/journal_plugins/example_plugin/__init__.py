from webapp import journal_plugins
from . import views
import webapp
import logging
logger = logging.getLogger(__name__)

class Plugin(journal_plugins.BasePlugin):
    name = 'Example Plugin'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('URL', self.url)
        self.manager.blueprint.add_url_rule(self.url, view_func=views.IndexView.as_view(f'{self.url_rule_base_name}.index'))
        logging.info('Registered Exmapel plugin view with url %s',self.url)

    def parse_entry(self, e):
        yield 'This is the output of the example plugin.'

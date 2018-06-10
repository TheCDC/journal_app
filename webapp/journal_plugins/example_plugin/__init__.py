from webapp.journal_plugins import classes
from . import views
import webapp
import logging
logger = logging.getLogger(__name__)

class Plugin(classes.BasePlugin):
    name = 'Example Plugin'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager.blueprint.add_url_rule(self.endpoint, view_func=views.IndexView.as_view(f'{self.url_rule_base_name}.index'))
        logger.info('Registered Exmaple plugin view with url %s', self.url)

    def parse_entry(self, e):
        yield 'This is the output of the example plugin.'

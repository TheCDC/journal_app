from webapp import parsing
from webapp import models


class Plugin(parsing.Plugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Example Plugin'
    @classmethod
    def parse_entry(cls, e: models.JournalEntry):
        # return ['test']
        return e.contents.split(' ')

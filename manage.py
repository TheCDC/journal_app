from webapp.journal_plugins.extensions import plugin_manager
from webapp import app
from webapp import models
from flask_script import Manager
import logging

logger = logging.getLogger(__name__)

manager = Manager(app)

@manager.command
def re_process_all_plugins():
    logging.warning('Long running operation has been initiated! All entries are being processed by plugins.')
    for e in models.JournalEntry.query.all():
        for item in (plugin_manager.parse_entry(e)):
            list(item['output'])
    logging.warning('All entries have been processed by plugins.')


def main():
    manager.run()

if __name__ == '__main__':
    main()

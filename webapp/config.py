import os
import logging

CONFIG_PATH = os.path.expanduser(os.path.join('~/', 'cdc_journal'))
#  ========== Logging ==========

LOG_PATH = os.path.join(CONFIG_PATH, 'journal_app.log')
try:
    os.makedirs(os.path.dirname(LOG_PATH))
    logging.info('created app data directory: %s', LOG_PATH)
except FileExistsError:
    pass

logger = logging.getLogger(__name__)

#  ========== Paths ==========
# hack to get a reference to the templates directory within the package
tmpl_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'templates')
ALEMBIC_PATH = os.path.join(CONFIG_PATH, 'migrations')
# set the database location and protocol
SQLITE_DB_PATH = os.path.join(CONFIG_PATH, 'database.db')

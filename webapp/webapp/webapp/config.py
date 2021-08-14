import os
import logging

IS_PRODUCTION = os.environ.get("IS_PRODUCTION", False)
if not IS_PRODUCTION:
    CONFIG_PATH = os.path.expanduser(
        os.path.join(os.path.dirname(__file__), "runtime_files")
    )
else:
    CONFIG_PATH = os.path.expanduser(os.path.join("~/", "cdc_journal"))

#  ========== Logging ==========

LOG_PATH = os.path.join(CONFIG_PATH, "journal_app.log")
try:
    os.makedirs(os.path.dirname(LOG_PATH))
    logging.info("created app data directory: %s", LOG_PATH)
except FileExistsError:
    pass

logger = logging.getLogger(__name__)

#  ========== Paths ==========
# hack to get a reference to the templates directory within the package
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
ALEMBIC_PATH = os.path.join(os.path.dirname(__file__), "migrations")
# set the database location and protocol
fallback_db_path = os.path.join(CONFIG_PATH, "database.db")
user = os.environ.get("POSTGRES_USER")
hostname = os.environ.get("POSTGRES_SERVER")
password = os.environ.get("POSTGRES_PASSWORD")
dbname = os.environ.get("POSTGRES_DB")
SQLALCHEMY_DATABASE_URI = f"postgresql://{user}:{password}@{hostname}/{dbname}:5432"
DEBUG_ENABLED = os.environ.get("DEBUG_ENABLED", False)

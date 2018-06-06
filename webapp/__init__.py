import logging
import logging.config
from webapp import config, forms, models
from webapp.models import db
from . import flask_app
logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(config.LOG_PATH)

handlers = [file_handler, stream_handler]

for h in handlers:
    h.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(levelname)-8s [%(name)-12s] %(asctime)s %(message)s')
    h.setFormatter(formatter)
    logger.addHandler(h)

logger.setLevel(logging.DEBUG)

# logging.config.fileConfig(config.LOG_PATH)


# alias to enable execution of this file from flask cli
app = flask_app.app



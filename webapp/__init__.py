import logging
import logging.config
from webapp import config

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(config.LOG_PATH)

handlers = [file_handler, stream_handler]

formatter = logging.Formatter(
    '%(levelname)-8s [%(name)-12s] %(asctime)s %(message)s')
for h in handlers:
    h.setFormatter(formatter)
    h.setLevel(logging.DEBUG)
    logger.addHandler(h)

logger.setLevel(logging.DEBUG)

from . import flask_app
# logging.config.fileConfig(config.LOG_PATH)

# alias to enable execution of this file from flask cli
app = flask_app.app

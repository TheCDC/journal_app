from webapp import config
import logging
import logging.config
from . import flask_app
# logging.config.fileConfig(config.LOG_PATH)

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(config.LOG_PATH)
formatter = logging.Formatter(
    '%(levelname)-8s [%(name)-12s] %(asctime)s %(message)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


# alias to enable execution of this file from flask cli
app = flask_app.app

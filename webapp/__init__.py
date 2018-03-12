from webapp import app_init
import logging

logging.basicConfig(
    filename=app_init.LOG_PATH,
    level=logging.DEBUG,
    format='[journal_app] %(asctime)s %(name)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.debug('Hello this is %s', __name__)

from . import flask_app

# alias to enable execution of this file from flask cli
app = flask_app.app

if __name__ == '__main__':
    logger.debug('%s is main', (__file__, ))
    app.main()

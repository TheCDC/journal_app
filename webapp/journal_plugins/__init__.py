import logging
from . import views
from .extensions import plugin_manager
logger = logging.getLogger(__name__)
from webapp import app
plugin_manager.init_app(app, view_func=views.ExampleView.as_view('plugins-index'))


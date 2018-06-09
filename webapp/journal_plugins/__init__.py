from flask import Blueprint

example_blueprint = Blueprint(
    'site',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/example_blueprint'
)

from . import views

example_blueprint.add_url_rule('/',view_func=views.ExampleView.as_view('index'))
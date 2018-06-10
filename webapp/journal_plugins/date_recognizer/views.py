from flask.views import MethodView
import flask
from . import models
class IndexView(MethodView):
    def get(self,**kwargs):
        return flask.render_template('date_recognizer/index.html')

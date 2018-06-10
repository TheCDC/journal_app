from flask.views import MethodView
import flask

class IndexView(MethodView):
    def get(self,**kwargs):
        return 'This is Example Plugin'
from flask.views import MethodView
import flask

class IndexView(MethodView):
    def get(self,**kwargs):
        return flask.render_template('example_plugin/index.html')
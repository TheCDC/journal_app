from flask.views import MethodView
import flask

class ExampleView(MethodView):
    def get(self,**kwargs):
        return flask.render_template('test.html', context=kwargs)
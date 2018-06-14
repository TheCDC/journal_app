from flask.views import MethodView
import flask
from . import models
from webapp.journal_plugins import extensions
import flask_login


class IndexView(MethodView):

    def get_context(self, **kwargs):
        context = dict(plugin=extensions.date_recognizer.to_dict())
        return context

    @flask_login.login_required
    def get(self, **kwargs):
        return flask.render_template('default_index.html', context=self.get_context(**kwargs))

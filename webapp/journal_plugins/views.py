from flask.views import MethodView
import flask
from .extensions import plugin_manager
from . import classes, models
import flask_login


class ExampleView(MethodView):
    def get_context(self, **kwargs):
        context = dict(plugins=list())
        preferences = plugin_manager.get_user_plugin_preferences(flask_login.current_user)
        for k, v in plugin_manager.plugins.items():
            context['plugins'].append(dict(plugin=v.to_dict(),preference=preferences[k]))
        return context

    @flask_login.login_required
    def get(self, **kwargs):
        return flask.render_template('journal_plugins_index.html', context=self.get_context(**kwargs))


class DefaultPluginIndexView(MethodView):
    @flask_login.login_required
    def get(self, **kwargs):
        return 'This plugin has no page.'


class PluginsSettingsOverviewView(MethodView):
    def get(self, **kwargs):
        return flask.render_template('plugins_settings_overview.html')
        pass


def add_views(plugin_manager: classes.PluginManager):
    plugin_manager.blueprint.add_url_rule('/settings',
                                          view_func=PluginsSettingsOverviewView.as_view('plugins-settings'))
    plugin_manager.blueprint.add_url_rule('', view_func=ExampleView.as_view(
        'plugins-index'))

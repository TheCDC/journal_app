from flask.views import MethodView
import flask
from .extensions import plugin_manager
from . import classes, models
import flask_login
from webapp.extensions import db


class IndexView(MethodView):
    def get_context(self, **kwargs):
        context = dict(plugins=list())
        preferences = plugin_manager.get_user_plugin_preferences(flask_login.current_user)
        for k, v in plugin_manager.plugins.items():
            context['plugins'].append(dict(plugin=v.to_dict(), preference=preferences[k]))
        return context

    @flask_login.login_required
    def get(self, **kwargs):
        return flask.render_template('journal_plugins_index.html', context=self.get_context(**kwargs))

    def post(self, **kwargs):
        # enable
        args = flask.request.form
        print(flask.request.form)
        target_id = args.get('enable-id', None)


        if target_id:
            target_id = int(target_id)
            print('Enable ', target_id)
            obj: models.UserPluginToggle = db.session.query(models.UserPluginToggle).filter(
                models.UserPluginToggle.id == target_id).first()
            obj.enabled = True
            db.session.add(obj)
            db.session.commit()
        target_id = args.get('disable-id', None)

        if target_id:
            target_id = int(target_id)
            print('Disable ', target_id)

            obj: models.UserPluginToggle = db.session.query(models.UserPluginToggle).filter(
                models.UserPluginToggle.id == target_id).first()
            obj.enabled = False
            db.session.add(obj)
            db.session.commit()
        return flask.redirect(flask.url_for('site.plugins-index'))


class DefaultPluginIndexView(MethodView):
    @flask_login.login_required
    def get(self, **kwargs):
        return 'This plugin has no page.'


class PluginsSettingsOverviewView(MethodView):
    def get_context(self, **kwargs):
        context = dict(plugins=list())
        preferences = plugin_manager.get_user_plugin_preferences(flask_login.current_user)
        for k, v in plugin_manager.plugins.items():
            context['plugins'].append(dict(plugin=v.to_dict(), preference=preferences[k]))
        return context

    @flask_login.login_required
    def get(self, **kwargs):
        return flask.render_template('plugins_settings_overview.html', context=self.get_context(**kwargs))


def add_views(plugin_manager: classes.PluginManager):
    plugin_manager.blueprint.add_url_rule('/shop',
                                          view_func=PluginsSettingsOverviewView.as_view('plugins-settings'))
    plugin_manager.blueprint.add_url_rule('', view_func=IndexView.as_view(
        'plugins-index'))

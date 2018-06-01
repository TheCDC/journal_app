from webapp.app_init import app, login_manager
from webapp import parsing
from . import views
from . import models
from . import api
import logging

logger = logging.getLogger(__name__)

# make functions available in templates
app.jinja_env.globals.update(link_for_entry=api.link_for_entry, )


@login_manager.user_loader
def load_user(target_id: int) -> models.User:
    return models.User.query.filter_by(id=int(target_id)).first()


@app.before_first_request
def setup_app():
    models.instantiate_db(app)
    parsing.PluginManager.init()


app.add_url_rule('/login', view_func=views.LoginView.as_view('login'))
app.add_url_rule('/logout', view_func=views.LogoutView.as_view('logout'))
app.add_url_rule('/register', view_func=views.RegisterView.as_view('register'))
app.add_url_rule('/home', view_func=views.HomeView.as_view('home'))
app.add_url_rule('/settings', view_func=views.SettingsView.as_view('settings'))
app.add_url_rule('/', view_func=views.IndexView.as_view('index'))

# generate endpoints for search view
search_view = views.EntrySearchView.as_view('entry')
delimiter = '-'
url_args = ['<int:year>', '<int:month>', '<int:day>']
# construct url endpoints for searching dates with increasing precision
for i in range(1, len(url_args) + 1):
    endpoint = '/entry/' + delimiter.join(url_args[:i])
    app.add_url_rule(endpoint, view_func=search_view)

login_manager.login_view = "login"

# ========== Plugin Views ==========
for p in parsing.PluginManager.registered_plugins:
    p.bootstrap_endpoint_onto_app('/plugin/', app)


def main():
    logger.info('run app')
    app.run(debug=True)

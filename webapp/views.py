import logging
import flask
from flask.views import MethodView
import datetime
from webapp.app_init import db
from webapp import models
from webapp import forms
from webapp import parsing
from webapp import api
import sqlalchemy
import flask.ext.login as login
logger = logging.getLogger(__name__)

if logger.disabled:
    raise RuntimeError('Logger is mistakenly disabled at top level')


class EnableLoggingMixin:
    def __init__(self, *args, **kwargs):
        classname = type(self).__name__
        super().__init__(*args, **kwargs)
        # self.logger = logging.getLogger(__name__ + '.IndexView')
        self._logger = logging.getLogger(__name__ + '.' + classname)

    @property
    def logger(self):
        if self._logger.disabled:
            self._logger.disabled = False
        return self._logger


class LoginView(MethodView):
    def get_template_name(self, ):
        return 'login.html'

    def get(self, **kwargs):
        context = dict(login_form=forms.LoginForm())
        context.update(kwargs)
        return flask.render_template(self.get_template_name(), context=context)

    def post(self, **kwargs):
        login_form = forms.LoginForm()
        context = dict(login_form=login_form)
        context.update(kwargs)
        found_user = models.User.query.filter_by(
            username=login_form.username.data,
            password=login_form.password.data).first()
        if found_user is not None:
            login.login_user(found_user)
            return flask.redirect(flask.url_for('index'))
        return self.get(error="User not found")


class LogoutView(MethodView):
    def get(self):
        login.logout_user()
        return flask.redirect(flask.url_for('index'))


class RegisterView(MethodView):
    def get_template_name(self, ):
        return 'register.html'

    def get(self, **kwargs):
        context = dict(register_form=forms.RegisterForm(), )
        context.update(kwargs)
        return flask.render_template(self.get_template_name(), context=context)

    def post(self):
        register_form = forms.RegisterForm()
        context = dict(register_form=register_form)
        if register_form.validate_on_submit():
            new_user = models.User(
                username=register_form.username.data,
                password=register_form.password.data,
                email=register_form.email.data)
            db.session.add(new_user)
            try:
                db.session.commit()
                login.login_user(new_user)
            except sqlalchemy.exc.IntegrityError:
                db.session.rollback()
                return self.get(
                    register_form=register_form, error="User already exists!")

            flask.flash('User successfully registered')
            return flask.redirect(flask.url_for('register'))
        else:
            return self.get(register_form=register_form)


class EntrySearchView(MethodView):
    def get_objects(self, **kwargs):
        start_date = self.args_to_date(**kwargs)
        found = list(
            db.session.query(models.JournalEntry).filter(
                models.JournalEntry.create_date >= start_date).order_by(
                    models.JournalEntry.create_date))
        return found

    def args_to_date(self,
                     year: int = None,
                     month: int = None,
                     day: int = None):

        start_date = datetime.datetime(1, 1, 1)
        if year is not None:
            start_date = start_date.replace(year=year)
        if month is not None:
            start_date = start_date.replace(month=month)
        if day is not None:
            start_date = start_date.replace(day=day)
        return start_date

    def get(self, **kwargs):
        # return a rendered entry if the date is fully specified
        my_kwargs = {
            k: kwargs[k]
            for k in ['year', 'month', 'day'] if k in kwargs
        }
        found = self.get_objects(**my_kwargs)
        breadcrumbs = [
            (api.link_for_date(**dict(list(my_kwargs.items())[:i + 1])),
             list(my_kwargs.values())[i]) for i in range(len(my_kwargs))
        ]
        if len(found) == 0:
            flask.abort(404)

        e = found[0]
        # handle incompletely specified date
        # take the user to a search
        if e.create_date != self.args_to_date(
                **my_kwargs) or len(breadcrumbs) < 3:
            return flask.render_template(
                'search_entry.html',
                context=dict(
                    search_results=[(e, api.link_for_entry(e)) for e in found],
                    breadcrumbs=breadcrumbs,
                ))
        forward = api.next_entry(e)
        backward = api.previous_entry(e)
        return flask.render_template(
            'entry.html',
            context=dict(
                entry=e,
                next_entry=forward,
                prev_entry=backward,
                plugin_manager=parsing.PluginManager,
                breadcrumbs=breadcrumbs,
            ))


class IndexView(MethodView, EnableLoggingMixin):
    def get_template_name(self):
        return 'index.html'

    def post(self, **kwargs):
        upload_form = forms.UploadForm()
        self.logger.debug('Try upload')
        good_parse = False
        if upload_form.validate_on_submit():
            logger.debug('Invalid form')
            file = flask.request.files[upload_form.file.name]
            session = db.session()
            try:
                parsed = parsing.identify_entries(
                    file.read().decode().split('\n'))
            except ValueError as e:
                # upload_form.file.errors
                self.logger.debug('parse failed')
                return self.get(upload_form=upload_form, error=e)

            db.session.query(models.JournalEntry).delete()
            for e in parsed:
                body_text = e.body.replace('\r', '')
                found = db.session.query(
                    models.JournalEntry).filter_by(create_date=e.date).first()
                if found:
                    found.contents = body_text
                else:
                    found = models.JournalEntry(
                        create_date=e.date, contents=body_text)
                session.add(found)

            session.flush()
            session.commit()
            self.logger.debug('parse succeeded')
            good_parse = True
        if good_parse:
            return self.get(
                upload_form=upload_form,
                success='Your journal was successfully parsed!')
        else:
            return self.get(
                upload_form=upload_form, error='Invalid submission!')
        # return flask.redirect(flask.url_for('index'))

    def get(self, **kwargs):
        upload_form = forms.UploadForm()

        latest_entry = api.get_latest_entry()
        # form the context with default values
        context = dict(
            upload_form=upload_form,
            entries_tree=api.get_entries_tree(),
            plugin_manager=parsing.PluginManager,
            latest_entry=latest_entry,
            now=datetime.datetime.now(),
            years=[(api.link_for_date(year=y.year), y.year)
                   for y in api.get_all_years()],
            error=None,
            success=None,
        )
        # allow context values to be overridden by kwargs
        context.update(kwargs)
        return flask.render_template(self.get_template_name(), context=context)

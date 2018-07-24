import webapp.models
from webapp import models
from webapp import forms
from webapp import api
from webapp import parsing

from webapp.extensions import db
from webapp.journal_plugins.extensions import plugin_manager
import logging
import flask
import datetime
import sqlalchemy
import flask_login
from flask.views import MethodView
from flask_security.utils import hash_password

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


class LogoutView(MethodView):
    def get(self):
        flask_login.logout_user()
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
            models.user_datastore.create_user(
                username=register_form.username.data,
                password=hash_password(register_form.password.data),
                email=register_form.email.data,
                first_name=register_form.first_name.data,
                last_name=register_form.last_name.data,
            )
            try:
                db.session.commit()
                flask_login.login_user(
                    models.user_datastore.get_user(register_form.email.data))
            except sqlalchemy.exc.IntegrityError:
                db.session.rollback()
                return self.get(
                    register_form=register_form, error="User already exists!")

            # flask.flash('User successfully registered')
            return flask.redirect(flask.url_for('home'))
        else:
            return self.get(register_form=register_form)


class EntrySearchView(MethodView):
    def get_objects(self, **kwargs):
        start_date = self.args_to_date(**kwargs)
        session = kwargs.get('session', db.session())

        found = list(flask_login.current_user.query_all_entries().filter(
            models.JournalEntry.create_date >= start_date).order_by(
            models.JournalEntry.create_date))
        return found

    def args_to_date(self,
                     year: int = None,
                     month: int = None,
                     day: int = None):

        start_date = datetime.date(1, 1, 1)
        if year is not None:
            start_date = start_date.replace(year=year)
        if month is not None:
            start_date = start_date.replace(month=month)
        if day is not None:
            start_date = start_date.replace(day=day)
        return start_date

    @flask_login.login_required
    def get(self, **kwargs):
        # return a rendered entry if the date is fully specified
        my_kwargs = {
            k: kwargs[k]
            for k in ['year', 'month', 'day'] if k in kwargs
        }
        try:
            found = self.get_objects(**my_kwargs)
        except ValueError:
            flask.abort(404)

        if len(found) == 0:
            flask.abort(404)

        e = found[0]
        plugins_output = list(plugin_manager.parse_entry(e))
        plugins_output.sort(key = lambda d: len(d['output']))
        session = db.session.object_session(flask_login.current_user)
        e = db.session.query(models.JournalEntry).filter(models.JournalEntry.id == e.id).first()
        for o in [e.next, e.previous]:
            if o:
                db.session.add(o)
        # plugins_output = [(obj['plugin']['name'], list(obj['output'])) for obj in plugin_manager.parse_entry(e)]
        context = dict(
            entry=models.journal_entry_schema.dump(obj=e).data,
            next=models.journal_entry_schema.dump(obj=e.next).data,
            previous=models.journal_entry_schema.dump(obj=e.previous).data,
            plugins_output=plugins_output,

        )
        try:
            if e.create_date != self.args_to_date(**my_kwargs):
                flask.abort(404)
        except ValueError:
            flask.abort(404)
        forward = e.next
        backward = e.previous
        return flask.render_template(
            'entry.html',
            context=context)


class IndexView(MethodView):
    def get_template_name(self):
        return 'index.html'

    def get(self):
        if flask_login.current_user.is_authenticated:
            return flask.redirect(flask.url_for('home'))
        return flask.render_template(self.get_template_name())


class HomeView(MethodView, EnableLoggingMixin):
    def get_template_name(self):
        return 'home.html'

    @flask_login.login_required
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

            flask_login.current_user.query_all_entries().delete()
            for e in parsed:
                body_text = e.body.replace('\r', '')
                found = flask_login.current_user.query_all_entries().filter_by(
                    create_date=e.date).first()
                if found:
                    found.contents = body_text
                else:
                    found = models.JournalEntry(
                        owner=flask_login.current_user,
                        create_date=e.date,
                        contents=body_text)
                plugin_manager.parse_entry(found)
                session.add(found)

            session.flush()
            session.commit()
            self.logger.debug('parse succeeded')
            good_parse = True
        if good_parse:
            # pre-calculate any plugins that happen to cache things.
            db.session.add(flask_login.current_user)

            q = list(flask_login.current_user.query_all_entries())

            for e in q:
                db.session.add(e)
                list(plugin_manager.parse_entry(e))
            return self.get(
                upload_form=upload_form,
                success='Your journal was successfully parsed!')
        else:
            return self.get(
                upload_form=upload_form, error='Invalid submission!')
        # return flask.redirect(flask.url_for('index'))

    @flask_login.login_required
    def get(self, **kwargs):
        upload_form = forms.UploadForm()
        try:
            db.session.add(flask_login.current_user)
        except sqlalchemy.exc.InvalidRequestError:
            pass
        latest_entry = db.session.query(models.JournalEntry).filter(models.JournalEntry.owner == flask_login.current_user).order_by(
            models.JournalEntry.create_date.desc()).first()
        # form the context with default values
        context = dict(
            upload_form=upload_form,
            entries_tree=api.get_entries_tree(flask_login.current_user),
            plugin_manager=plugin_manager,
            latest_entry=models.journal_entry_schema.dump(obj=latest_entry).data,
            now=datetime.datetime.now(),
            days_since_latest=(
                    datetime.datetime.now().date() - latest_entry.create_date).days if latest_entry else None,
            error=None,
            success=None,
            num_entries = db.session.query(models.JournalEntry).filter(models.JournalEntry.owner == flask_login.current_user).count()
        )
        # allow context values to be overridden by kwargs and request
        context.update(kwargs)
        for key in context:
            if key in flask.request.args:
                context[key] = flask.request.args.get(key)
        db.session.close()
        return flask.render_template(self.get_template_name(), context=context)


class SettingsView(MethodView):
    def get_template_name(self):
        return 'settings.html'

    @flask_login.login_required
    def get(self, **kwargs):

        # form = flask_login.current_user.get_settings_form()
        form = kwargs.get('form', None)
        if not form:
            form = forms.UserEditForm(**api.object_as_dict(flask_login.current_user), obj=flask_login.current_user)
        context = dict(settings_form=form)

        context.update(kwargs)
        return flask.render_template(self.get_template_name(), context=context)

    @flask_login.login_required
    def post(self):
        cu = flask_login.current_user
        form = forms.UserEditForm(obj=cu)
        if form.validate_on_submit():
            session = db.session()
            cu.first_name = form.first_name.data
            cu.last_name = form.last_name.data
            cu.email = form.email.data
            session.add(cu)
            session.commit()
            # cu.update_settings(form)
        else:
            return flask.render_template(context=dict(settings_form=form))
        return flask.redirect(flask.url_for('settings'))


class EntryEditView(MethodView):
    @flask_login.login_required
    def get(self, **kwargs):
        found = models.JournalEntry.query.filter_by(id=kwargs['id'], owner=flask_login.current_user).first()
        if not found:
            flask.abort(404)
        form = forms.JournalEntryEditForm(**api.object_as_dict(found))
        context = dict(create=False, heading='Edit Entry')
        context['heading'] = 'Edit entry'
        context.update(dict(back=api.link_for_entry(found), action=flask.url_for('edit_entry', id=form.id.data),
                            form=form))
        context.update(kwargs)
        db.session.close()
        return flask.render_template('edit_entry.html', context=context)

    @flask_login.login_required
    def post(self, **kwargs):
        form = forms.JournalEntryEditForm(**flask.request.form)
        cu = flask_login.current_user
        context = dict(errors=list())
        if form.validate_on_submit():
            if form.owner_id.data == cu.id:
                obj = models.JournalEntry.query.filter_by(id=form.id.data, owner=cu).first()
                form.populate_obj(obj)
                session = db.session()
                session.add(obj)
                session.commit()

                return flask.redirect(api.link_for_entry(obj))
            else:
                flask.abort(403)
        else:
            context['errors'].append('form invalid')
            return self.get(**context)


class EntryCreateView(MethodView):
    @flask_login.login_required
    def get(self, **kwargs):
        context = dict(
            create=True, back=flask.url_for('home'), action=flask.url_for('create_entry'),
            heading='Create Entry'
        )
        form = forms.JournalEntryCreateForm()
        form.contents.data = ''
        context.update(dict(form=form))
        context.update(**kwargs)
        return flask.render_template('edit_entry.html', context=context)

    @flask_login.login_required
    def post(self, **kwargs):
        form = forms.JournalEntryCreateForm(**flask.request.form)
        context = dict(form=form, errors=[])
        context.update(**kwargs)
        if form.validate_on_submit():
            obj = models.JournalEntry(owner=flask_login.current_user)
            form.populate_obj(obj)
            print('obj', obj.owner)
            session = db.session()
            try:
                session.add(obj)
                session.commit()
            except sqlalchemy.exc.IntegrityError:
                session.rollback()
                context['errors'].append('That date already has an entry!')
                return self.get(**context)

            return flask.redirect(api.link_for_entry(flask_login.current_user.get_latest_entry()))

        else:
            return self.get(**context)


class ExportJournalView(MethodView):
    @flask_login.login_required
    def get(self, **kwargs):
        cu: models.User = flask_login.current_user
        entries = models.JournalEntry.query.filter_by(owner=cu).order_by(models.JournalEntry.create_date)

        def generate():
            for e in entries:
                yield e.date_string
                yield '\n'
                yield e.contents
                yield '\n'

        response = flask.Response(flask.stream_with_context(generate()))
        vals = [cu.first_name,cu.last_name]
        tokens = []
        for v in vals:
            if v:
                tokens.append(v)
        tokens.extend([cu.email,f'journal exported {datetime.datetime.now().isoformat()}.txt'])
        filename = ' '.join(tokens)
        cd = f'attachment; filename="{filename}"'
        response.headers['Content-Disposition'] = cd
        response.mimetype = 'application/octet-stream'
        return response


class DeleteEntryView(MethodView):
    def post(self, **kwargs):
        session = db.session()
        cu = flask_login.current_user
        obj = models.JournalEntry.query.filter_by(id=kwargs['id']).first()
        if not obj:
            flask.abort(404)
        if cu == obj.owner:
            old_date = obj.date_string
            session.delete(obj)
        session.commit()
        return flask.redirect(flask.url_for('home', success=f'Deleted entry for {old_date}'))

    def get(self,**kwargs):
        my_id = kwargs['id']

        obj = models.JournalEntry.query.filter_by(id=my_id).first()

        context = dict(entry=obj,
                       delete_url=flask.url_for('delete_entry',id=my_id),
                       back_url=api.link_for_entry(obj))
        return flask.render_template('delete_entry.html',context=context)


class LatestView(MethodView):
    def get(self, **kwargs):
        u = flask_login.current_user
        latest = u.get_latest_entry()
        print('latest', latest)
        print('user', u.query_all_entries().order_by(
            models.JournalEntry.create_date.desc()).first())
        if latest is not None:
            return flask.redirect(api.link_for_entry(latest))
        else:
            flask.abort(404)
class PrivacyPolicyView(MethodView):
    def get(self,**kwargs):
        return flask.render_template('privacy.html')

def add_views(app):
    app.add_url_rule('/', view_func=IndexView.as_view('index'))
    app.add_url_rule('/register', view_func=RegisterView.as_view('register'))
    app.add_url_rule('/home', view_func=HomeView.as_view('home'))
    app.add_url_rule('/latest', view_func=LatestView.as_view('latest_entry'))
    app.add_url_rule('/export', view_func=ExportJournalView.as_view('export_journal'))
    app.add_url_rule('/settings', view_func=SettingsView.as_view('settings'))
    app.add_url_rule('/privacy', view_func=PrivacyPolicyView.as_view('privacy'))
    app.add_url_rule('/edit/new', view_func=EntryCreateView.as_view('create_entry'))
    app.add_url_rule('/edit/<int:id>', view_func=EntryEditView.as_view('edit_entry'))
    app.add_url_rule('/delete/<int:id>', view_func=DeleteEntryView.as_view('delete_entry'))

    # generate endpoints for search view
    search_view = EntrySearchView.as_view('entry')
    delimiter = '-'
    url_args = ['<int:year>', '<int:month>', '<int:day>']
    # construct url endpoints for searching dates with increasing precision
    endpoint = '/entry/' + delimiter.join(url_args)
    app.add_url_rule(endpoint, view_func=search_view)

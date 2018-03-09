import flask
from flask.views import View, MethodView
import datetime
from webapp.app_init import app, db
from webapp import models
from webapp import forms
from webapp import parsing
from webapp import parsing_plugins
from webapp import api


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


class IndexView(MethodView):
    def get_template_name(self):
        return 'index.html'

    def post(self):
        form = forms.UploadForm()
        if form.validate_on_submit():
            print('Validated!')
            file = flask.request.files[form.file.name]
            session = db.session()
            db.session.query(models.JournalEntry).delete()
            for e in parsing.identify_entries(
                    file.read().decode().split('\n')):
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
            return flask.redirect(flask.url_for('index'))

    def get(self, **kwargs):
        form = forms.UploadForm()

        all_entries = list(
            db.session.query(models.JournalEntry).order_by(
                models.JournalEntry.create_date))
        entries_tree = dict()
        for e in all_entries:
            y = e.create_date.year
            m = e.create_date.month
            if y not in entries_tree:
                entries_tree[y] = dict()
            if m not in entries_tree[y]:
                entries_tree[y][m] = list()
            entries_tree[y][m].append(e)

        return flask.render_template(
            'index.html',
            context=dict(
                form=form,
                entries_tree=entries_tree,
                plugin_manager=parsing.PluginManager,
                years=[(api.link_for_date(year=y.year), y.year)
                       for y in api.get_all_years()]))

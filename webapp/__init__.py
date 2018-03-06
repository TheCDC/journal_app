import flask
from webapp.app_init import app, db
from webapp import forms
import webapp.models as models
from webapp import parsing
from webapp import parsing_plugins
import datetime
from flask import request
from flask.views import View, MethodView

parsing.PluginManager.init()
def link_for_date(**kwargs):
    expected = ['year', 'month', 'day']
    d = {k: kwargs[k] for k in expected if k in kwargs}
    return flask.url_for('entry', **d)


def link_for_entry(entry: models.JournalEntry):
    return link_for_date(
        year=entry.create_date.year,
        month=entry.create_date.month,
        day=entry.create_date.day)


def get_latest_entry():
    return db.session.query(models.JournalEntry).order_by(
        models.JournalEntry.create_date.desc()).first()


def get_all_years():
    start_year = db.session.query(models.JournalEntry).order_by(
        models.JournalEntry.create_date).first()
    end_year = db.session.query(models.JournalEntry).order_by(
        models.JournalEntry.create_date.desc()).first()
    if start_year and end_year:
        for y in range(start_year.create_date.year,
                       end_year.create_date.year + 1):
            yield datetime.datetime(y, 1, 1, 0, 0)


def next_entry(e: models.JournalEntry):
    return db.session.query(models.JournalEntry).filter(
        models.JournalEntry.create_date > e.create_date).first()


def previous_entry(e: models.JournalEntry):
    return db.session.query(models.JournalEntry).filter(
        models.JournalEntry.create_date < e.create_date).order_by(
            models.JournalEntry.create_date.desc()).first()


app.jinja_env.globals.update(
    link_for_entry=link_for_entry,
    get_latest_entry=get_latest_entry,
    get_all_years=get_all_years)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = forms.UploadForm(flask.request.form)

    if flask.request.method == 'POST':
        form = forms.UploadForm(flask.request.form)
        print('vars(form.file)', vars(form.file))
        if form.validate():
            print('Validated!')
        print('files', flask.request.files)
        file = flask.request.files[form.file.name]
        # print('file', vars(file))
        session = db.session()
        db.session.query(models.JournalEntry).delete()
        for e in parsing.identify_entries(file.read().decode().split('\n')):
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
        # print('file', file.read())
        return flask.redirect(flask.url_for('index'))
    all_entries = list(
        db.session.query(models.JournalEntry).order_by(
            models.JournalEntry.create_date))

    return flask.render_template(
        'index.html',
        context=dict(
            form=form,
            entries=all_entries,
            plugin_manager=parsing.PluginManager,
            years=[(link_for_date(year=y.year), y.year)
                   for y in get_all_years()]))


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
        print('my_kwargs', my_kwargs, len(my_kwargs))
        breadcrumbs = [(link_for_date(**dict(list(my_kwargs.items())[:i + 1])),
                        list(my_kwargs.values())[i])
                       for i in range(len(my_kwargs))]
        print('breadcrumbs', breadcrumbs)
        e = found[0]
        # handle incompleteley specified date
        # take the user to a search
        if e.create_date != self.args_to_date(
                **my_kwargs) or len(breadcrumbs) < 3:
            return flask.render_template(
                'search_entry.html',
                context=dict(
                    search_results=[(e, link_for_entry(e)) for e in found],
                    breadcrumbs=breadcrumbs,
                ))
        forward = next_entry(e)
        backward = previous_entry(e)
        return flask.render_template(
            'entry.html',
            context=dict(
                entry=e,
                next_entry=forward,
                prev_entry=backward,
                plugin_manager=parsing.PluginManager,
                breadcrumbs=breadcrumbs,
            ))


search_view = EntrySearchView.as_view('entry')
app.add_url_rule('/entry/<int:year>', view_func=search_view)
app.add_url_rule('/entry/<int:year>/<int:month>', view_func=search_view)
app.add_url_rule(
    '/entry/<int:year>/<int:month>/<int:day>', view_func=search_view)


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()

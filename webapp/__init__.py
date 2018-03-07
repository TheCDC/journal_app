import flask
from webapp.app_init import app, db
from webapp import forms
import webapp.models as models
from webapp import parsing
from webapp import parsing_plugins
import datetime
from flask import request
from flask.views import View, MethodView



def link_for_date(**kwargs):
    """Return the app's link for the given date.
    The date is given as keyuword arguments (year, month,day)."""
    expected = ['year', 'month', 'day']
    d = {k: kwargs[k] for k in expected if k in kwargs}
    return flask.url_for('entry', **d)


def link_for_entry(entry: models.JournalEntry):
    """Return the app's link for the given journal entry.
    This function is a shortcut for link_for_date."""
    return link_for_date(
        year=entry.create_date.year,
        month=entry.create_date.month,
        day=entry.create_date.day)


def get_latest_entry() -> models.JournalEntry:
    """Return the chronologically latest JournalEntry."""
    return db.session.query(models.JournalEntry).order_by(
        models.JournalEntry.create_date.desc()).first()


def get_all_years() -> 'iterable[datetime.datetime]':
    """Return a list of dates corresponding to the range of
    years encompassed by all journal entries."""
    start_year = db.session.query(models.JournalEntry).order_by(
        models.JournalEntry.create_date).first()
    end_year = db.session.query(models.JournalEntry).order_by(
        models.JournalEntry.create_date.desc()).first()
    if start_year and end_year:
        for y in range(start_year.create_date.year,
                       end_year.create_date.year + 1):
            yield datetime.datetime(y, 1, 1, 0, 0)


def next_entry(e: models.JournalEntry) -> models.JournalEntry:
    """Return the first JournalEntry that falls chronologically after
    the given entry."""
    return db.session.query(models.JournalEntry).filter(
        models.JournalEntry.create_date > e.create_date).first()


def previous_entry(e: models.JournalEntry) -> models.JournalEntry:
    """Return the first JournalEntry that falls chronologically before
    the given entry."""
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
        if form.validate():
            print('Validated!')
        file = flask.request.files[form.file.name]
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
        breadcrumbs = [(link_for_date(**dict(list(my_kwargs.items())[:i + 1])),
                        list(my_kwargs.values())[i])
                       for i in range(len(my_kwargs))]
        try:
            e = found[0]
        except IndexError:
            flask.abort(404)
        # handle incompletely specified date
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
url_args = '<int:year>/<int:month>/<int:day>'.split('/')
# construct url endpoints for searching dates with increasing precision
for i in range(1, len(url_args) + 1):
    endpoint = '/entry/' + '/'.join(url_args[:i])
    app.add_url_rule(endpoint, view_func=search_view)


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()

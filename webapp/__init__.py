import flask
from webapp.app_init import app, db
from webapp import forms
import webapp.models as models
from webapp import parsing
from webapp import parsing_plugins
import datetime
from flask import request
from . import views


@app.before_first_request
def setup_app():
    models.instantiate_db(app)
    parsing.PluginManager.init()


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
    # define earliest and latest years of entries
    start_year = db.session.query(models.JournalEntry).order_by(
        models.JournalEntry.create_date).first()
    end_year = db.session.query(models.JournalEntry).order_by(
        models.JournalEntry.create_date.desc()).first()
    if start_year and end_year:
        for y in range(start_year.create_date.year,
                       end_year.create_date.year + 1):
            # find any entry within this year but before next year
            found = db.session.query(models.JournalEntry).filter(
                models.JournalEntry.create_date >= datetime.datetime(
                    y, 1, 1, 0, 0)).filter(
                        models.JournalEntry.create_date < datetime.datetime(
                            y + 1, 1, 1, 0, 0)).first()
            # only yield this year if has an entry
            if found:
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
            years=[(link_for_date(year=y.year), y.year)
                   for y in get_all_years()]))


search_view = views.EntrySearchView.as_view('entry')
url_args = '<int:year>/<int:month>/<int:day>'.split('/')
# construct url endpoints for searching dates with increasing precision
for i in range(1, len(url_args) + 1):
    endpoint = '/entry/' + '/'.join(url_args[:i])
    app.add_url_rule(endpoint, view_func=search_view)


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()

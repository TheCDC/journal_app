import flask
from flask.views import View, MethodView
import datetime
from webapp.app_init import app, db
from webapp import models
from webapp import parsing


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
class IndexView(MethodView):

    def get_template_name(self):
        return 'entry.html'

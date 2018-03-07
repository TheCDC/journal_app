from webapp.app_init import db, admin
from flask_admin.contrib.sqla import ModelView
import datetime
from webapp import parsing


class JournalEntry(db.Model):
    """Model for journal entries."""
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    contents = db.Column(db.String)

    def __str__(self):
        return str(self.id)

    def to_html(self):
        """Return HTML necesary to render the entry the same as plain text."""
        return self.contents.replace('\n', '<br>')

    @property
    def tokens(self):
        """Return the contents parsed as tokens."""
        raise NotImplementedError(
            'TODO: tokenize entry contents to allow for wiki-style linking.')

    @property
    def date_string(self):
        """Date as YYYY-MM-DD."""
        return self.create_date.strftime('%Y-%m-%d')

    @property
    def date_human(self):
        """A pretty and human readable date."""
        return self.create_date.strftime('%B %d, %Y')


class PluginConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    class_name = db.Column(db.String)
    enabled = db.Column(db.Boolean, default=True)
    name = db.Column(db.String)


class JournalEntryView(ModelView):
    column_list = (
        'create_date',
        'contents',
    )

    def summary(view, context, model, name):
        s = model.contents
        return s[:30] + (len(s) > 30) * '...'

    column_formatters = {
        'contents': summary,
    }


admin.add_view(JournalEntryView(JournalEntry, db.session))
admin.add_view(ModelView(PluginConfig, db.session))

from webapp.app_init import db, admin
from flask_admin.contrib.sqla import ModelView
import datetime
from webapp import parsing


class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    contents = db.Column(db.String)

    def __str__(self):
        return str(self.id)

    def to_html(self):
        return self.contents.replace('\n', '<br>')

    @property
    def tokens(self):
        raise NotImplementedError('TODO: tokenize entry contents to allow for wiki-style linking.')

    @property
    def date_string(self):
        return self.create_date.strftime('%Y-%m-%d')


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

from webapp.app_init import db, admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.sql import func
import datetime


class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    contents = db.Column(db.String)

    def __str__(self):
        return str(self.id)


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

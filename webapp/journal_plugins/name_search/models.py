from webapp import extensions
from webapp import models

import datetime
from sqlalchemy.orm import backref
from webapp.journal_plugins import name_search

db = extensions.db


class NameSearchCache(db.Model):
    parent_id = db.Column(db.Integer, db.ForeignKey(models.JournalEntry.id, ondelete="cascade"), primary_key=True, nullable=False)
    parent = db.relationship(models.JournalEntry,foreign_keys='NameSearchCache.parent_id')
    created_at = db.Column(
        db.Date, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.Date, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    json = db.Column(db.String)

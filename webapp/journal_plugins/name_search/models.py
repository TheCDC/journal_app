from webapp import extensions
from webapp import models

import datetime
from sqlalchemy.sql import func

from sqlalchemy.orm import backref
from webapp.journal_plugins import name_search

db = extensions.db


class NameSearchCache(db.Model):
    parent_id = db.Column(db.Integer, db.ForeignKey(models.JournalEntry.id, ondelete="cascade"), primary_key=True,)
    parent = db.relationship(models.JournalEntry, foreign_keys='NameSearchCache.parent_id')
    created_at = db.Column(
        db.DateTime, default=func.now(),nullable=False)
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now(),nullable=False)
    json = db.Column(db.String)

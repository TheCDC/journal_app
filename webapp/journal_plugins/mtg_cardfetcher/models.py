
from webapp import extensions
from webapp import models

from sqlalchemy.sql import func

db = extensions.db


class MTGCardFetcherCache(db.Model):
    parent_id = db.Column(db.Integer, db.ForeignKey(models.JournalEntry.id, ondelete="cascade"), primary_key=True,)
    parent = db.relationship(models.JournalEntry, foreign_keys='MTGCardFetcherCache.parent_id')
    created_at = db.Column(
        db.DateTime, default=func.now(),nullable=False)
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now(),nullable=False)
    json = db.Column(db.String)

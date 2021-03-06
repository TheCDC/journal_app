from webapp import extensions
from webapp import models
from sqlalchemy.sql import func

db = extensions.db


class UserPluginToggle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(models.User.id, ondelete="cascade"))
    plugin_name = db.Column(db.String)
    enabled = db.Column(db.Boolean, default=True)
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now(), nullable=False,
        server_default=func.now())
    created_at = db.Column(
        db.Date, default=func.now(), index=True)
    __table_args__ = (db.UniqueConstraint('user_id', 'plugin_name', name='_user_plugin_preference'),)


class PluginOutputCache(db.Model):
    """Document store for plugin output"""
    id = db.Column(db.Integer, primary_key=True)

    parent_id = db.Column(db.Integer, db.ForeignKey(models.JournalEntry.id, ondelete="cascade"), )
    plugin_name = db.Column(db.String)
    parent = db.relationship(models.JournalEntry, foreign_keys='PluginOutputCache.parent_id')
    created_at = db.Column(
        db.DateTime, default=func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    json = db.Column(db.String)
    schema_version = db.Column(db.Integer)


# ========== Marshmallow Schemas ==========

class UserPluginToggleSchema(extensions.marshmallow.ModelSchema):
    class Meta:
        model = UserPluginToggle


user_plugin_toggle_schema = UserPluginToggleSchema()

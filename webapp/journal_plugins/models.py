from webapp import extensions
from webapp import models
from sqlalchemy.sql import func



db = extensions.db


class UserPluginToggle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(models.User.id,ondelete="cascade"))
    plugin_name = db.Column(db.String)
    enabled = db.Column(db.Boolean, default=True)
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now(), nullable=False,
        server_default=func.now())
    created_at = db.Column(
        db.Date, default=func.now(), index=True)


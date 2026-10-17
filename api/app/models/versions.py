from sqlalchemy.sql import func
from ..extensions import db
from .base.mixins import TransactionalMixin


class Version(db.Model, TransactionalMixin):
    __tablename__ = 'versions'

    # Base columns >>
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    active = db.Column(db.Boolean(), nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now()) 
    # Custom columns >>
    description = db.Column(db.String(), nullable=False)
    # Relationships >>

    # Properties >>
    

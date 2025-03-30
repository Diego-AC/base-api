from marshmallow import fields
from src.extensions import ma, db
from datetime import datetime

class BaseAutoSchema(ma.SQLAlchemyAutoSchema):
    """Clase base para aplicar la serialización de DateTime de manera global con SQLAlchemyAutoSchema."""

    def on_bind_field(self, field_name, field_obj):
        if isinstance(field_obj, fields.DateTime):
            field_obj.format = '%d/%m/%Y %H:%M:%S'  # Formato personalizado

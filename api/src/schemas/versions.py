from marshmallow import fields, Schema
from .base.custom_schema import BaseAutoSchema
from src.extensions import ma
from src.models.versions import Version


class VersionSerializer(BaseAutoSchema):
    class Meta:
        model = Version
        load_instance = False
        # exclude = []
        # include_fk = False


class PayloadVersionSchema(Schema):
    description = fields.Str(required=True)
    status = fields.Int(nullable=False)
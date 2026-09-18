from marshmallow import fields, Schema
from .base.custom_schema import BaseAutoSchema
from ..extensions import ma
from ..models.versions import Version


class VersionSerializer(BaseAutoSchema):
    class Meta:
        model = Version
        load_instance = False
        # exclude = []
        # include_fk = False


class PayloadVersionSchema(Schema):
    description = fields.Str(required=True)
    active = fields.Int()
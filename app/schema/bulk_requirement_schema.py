from marshmallow import fields, Schema, EXCLUDE
from app.schema.requirement import RequirementSchema


class BulkRequirementSchema(Schema):

    class Meta:
        unknown = EXCLUDE

    items = fields.List(
        fields.Nested(RequirementSchema),
        required=True,
        validate=lambda lst: len(lst) > 0
    )

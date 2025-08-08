from marshmallow import fields, Schema, EXCLUDE


def make_bulk_schema(nested_cls):
    class BulkRequirementSchema(Schema):
        class Meta:
            unknown = EXCLUDE

        items = fields.List(
            fields.Nested(nested=nested_cls),
            required=True,
            validate=lambda lst: len(lst) > 0
        )

    return BulkRequirementSchema()

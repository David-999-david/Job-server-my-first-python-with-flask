from marshmallow import Schema, validate, EXCLUDE, fields


class RequirementSchema(Schema):

    class Meta:
        unknown = EXCLUDE

    jobId = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

    addressId = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1)
    )

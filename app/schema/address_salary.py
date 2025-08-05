from marshmallow import Schema, fields, validate, EXCLUDE


class AddressSalarySchema(Schema):

    class Meta:
        Unknown = EXCLUDE

    jobId = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

    street = fields.Str(
        required=True,
        validate=validate.Length(min=1)
    )

    city = fields.Str(
        required=True,
        validate=validate.Length(min=1)
    )

    country = fields.Str(
        required=True,
        validate=validate.Length(min=1)
    )

    amount = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=0)
    )

from marshmallow import Schema, fields, validate, EXCLUDE


class WorkerSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1)
    )

    email = fields.Str(
        required=False,
        validate=validate.Length(min=1)
    )

    phone = fields.Str(
        required=True,
        validate=validate.Length(min=1)
    )


class JoinJobwithWorkerSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    jobId = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )
    workerId = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )
    salary = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=0.01)
    )

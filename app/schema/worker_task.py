from marshmallow import Schema, fields, validate, EXCLUDE, pre_load

Task_Status = ("pending", "processing", "completed", "canceled")


class worker_task_schema(Schema):
    class Meta:
        unknown = EXCLUDE

    worker_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )
    task_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )


class task_staus_schema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.String(
        required=True,
        validate=validate.OneOf(Task_Status)
    )

    @pre_load
    def strip_normalize(self, data, **kwargs):
        if isinstance(data.get('status'), str):
            data['status'] = data['status'].strip()
            data['status'] = data['status'].lower()
        return data

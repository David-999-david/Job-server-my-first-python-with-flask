from marshmallow import Schema, fields, validate, pre_load, EXCLUDE

FREQUENCIES = ("daily", "weekly", "monthly")


class taskSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    title = fields.String(
        required=True,
        validate=validate.Length(min=1)
    )
    description = fields.String(
        required=True,
        validate=validate.Length(min=1)
    )
    type = fields.String(
        required=True,
        validate=validate.OneOf(FREQUENCIES)
    )

    @pre_load
    def strip_normalize(self, data, **kwargs):
        if isinstance(data.get("title"), str):
            data['title'] = data['title'].strip()
        if isinstance(data.get('description'), str):
            data['description'] = data['description'].strip()
        if isinstance(data.get('type'), str):
            data['type'] = data['type'].strip().lower()
        return data


def bulk_tasks_schema(nested_class):

    class TasksSchema(Schema):
        class Meta:
            unknown = EXCLUDE

        items = fields.List(
            fields.Nested(nested_class),
            required=True,
            validate=lambda lst: len(lst) > 0
        )
    return TasksSchema()

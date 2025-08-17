from marshmallow import Schema, fields, pre_load, validate, EXCLUDE


def bulk_items_schema(nested_schema):
    class items_schema(Schema):
        class Meta:
            unknown = EXCLUDE
        items = fields.List(
            fields.Nested(nested_schema),
            required=True,
            validate=validate.Length(min=1)
        )
    return items_schema()


class category_schema(Schema):
    class Meta:
        unknown = EXCLUDE
    name = fields.String(
        required=True,
        validate=validate.Length(min=1)
    )

    @pre_load
    def strip_normailze(self, data, **kwargs):
        if isinstance(data.get('name'), str):
            data['name'] = data['name'].strip()
        return data


class sub_category_schema(Schema):
    class Meta:
        unknown = EXCLUDE
    category_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )
    name = fields.String(
        required=True,
        validate=validate.Length(min=1)
    )

    @pre_load
    def strip_normalize(self, data, **kwargs):
        if isinstance(data.get('name'), str):
            data['name'] = data['name'].strip()
        return data


class TaskSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    title = fields.String(
        required=True,
        validate=validate.Length(min=1)
    )
    description = fields.String(
        required=True,
        validate=validate.Length(min=5)
    )
    image_url = fields.String(
        required=True
    )


class ProjectSchema(Schema):

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
    sub_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    @pre_load
    def strip_normazlie(self, data, **kwargs):
        for k in ("title", "description"):
            if k in data and isinstance(data.get(k), str):
                data[k] = data[k].strip()
        return data

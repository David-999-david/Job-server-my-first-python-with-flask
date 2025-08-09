from marshmallow import Schema, fields, validate, EXCLUDE, validates, pre_load
from marshmallow import ValidationError
import re

E164 = re.compile(r"^\+?[1-9]\d{1,14}$")


class RegisterSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(
        required=True,
        validate=validate.Length(min=1)
    )
    email = fields.Email(
        required=True,
    )
    phone = fields.String(
        required=False,
        allow_none=True
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=8)
    )

    @pre_load
    def strip_and_normalize(self, data, **kwargs):
        for k in ("name", "email", "phone", "password"):
            if k in data and isinstance(data[k], str):
                data[k] = data[k].strip()
        if "email" in data and isinstance(data["email"], str):
            data["email"] = data["email"].lower()
        if data.get('phone') in ('', None):
            data['phone'] = None
        return data

    @validates("phone")
    def check_phone(self, value, **kwargs):
        if value is None or value == "":
            return
        if not E164.match(value):
            raise ValidationError("Phone must be E164 disign")


class LoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(
        required=True,
    )

    password = fields.String(
        required=True,
        validate=validate.Length(min=8)
    )

    @pre_load
    def Strip_and_normalize(self, data, **kwargs):
        for k in ("email", "password"):
            if k in data and isinstance(data[k], str):
                data[k] = data[k].strip()
        if "email" in data and isinstance(data['email'], str):
            data['email'] = data['email'].lower()
        return data

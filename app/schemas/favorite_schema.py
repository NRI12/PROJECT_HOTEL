from marshmallow import Schema, fields, validate


class FavoriteCreateSchema(Schema):
    hotel_id = fields.Integer(required=True, validate=validate.Range(min=1))


from marshmallow import Schema, fields


class NotificationReadSchema(Schema):
    is_read = fields.Boolean(load_default=True)


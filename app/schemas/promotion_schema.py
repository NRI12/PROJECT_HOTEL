from marshmallow import Schema, fields, validate

class PromotionCreateSchema(Schema):
    hotel_id = fields.Integer(allow_none=True)
    room_id = fields.Integer(allow_none=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True)
    discount_type = fields.String(required=True, validate=validate.OneOf(['percentage', 'fixed']))
    discount_value = fields.Decimal(required=True, as_string=False, validate=validate.Range(min=0))
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)
    applicable_days = fields.String(allow_none=True)
    min_nights = fields.Integer(allow_none=True, validate=validate.Range(min=1))

class PromotionUpdateSchema(Schema):
    title = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True)
    discount_type = fields.String(validate=validate.OneOf(['percentage', 'fixed']))
    discount_value = fields.Decimal(as_string=False, validate=validate.Range(min=0))
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    applicable_days = fields.String(allow_none=True)
    min_nights = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    is_active = fields.Boolean()
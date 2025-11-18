from marshmallow import Schema, fields, validate

class DiscountCreateSchema(Schema):
    code = fields.String(required=True, validate=validate.Length(min=1, max=50))
    description = fields.String(allow_none=True)
    discount_type = fields.String(required=True, validate=validate.OneOf(['percentage', 'fixed']))
    discount_value = fields.Decimal(required=True, as_string=False, validate=validate.Range(min=0))
    min_order_amount = fields.Decimal(allow_none=True, as_string=False, validate=validate.Range(min=0))
    max_discount_amount = fields.Decimal(allow_none=True, as_string=False, validate=validate.Range(min=0))
    usage_limit = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)

class DiscountUpdateSchema(Schema):
    code = fields.String(validate=validate.Length(min=1, max=50))
    description = fields.String(allow_none=True)
    discount_type = fields.String(validate=validate.OneOf(['percentage', 'fixed']))
    discount_value = fields.Decimal(as_string=False, validate=validate.Range(min=0))
    min_order_amount = fields.Decimal(allow_none=True, as_string=False, validate=validate.Range(min=0))
    max_discount_amount = fields.Decimal(allow_none=True, as_string=False, validate=validate.Range(min=0))
    usage_limit = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    is_active = fields.Boolean()

class DiscountValidateSchema(Schema):
    code = fields.String(required=True)
    order_amount = fields.Decimal(required=True, as_string=False, validate=validate.Range(min=0))
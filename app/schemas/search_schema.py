from marshmallow import Schema, fields, validates, ValidationError, validate, INCLUDE
from datetime import date

class SearchSchema(Schema):
    destination = fields.Str(required=False, allow_none=True)
    check_in = fields.Date(required=False, allow_none=True)
    check_out = fields.Date(required=False, allow_none=True)
    num_guests = fields.Int(required=False, allow_none=True)
    min_price = fields.Float(required=False, allow_none=True)
    max_price = fields.Float(required=False, allow_none=True)
    star_rating = fields.Int(required=False, allow_none=True)
    star_ratings = fields.List(fields.Int(), required=False)
    amenity_ids = fields.List(fields.Int(), required=False)
    free_cancel = fields.Boolean(required=False)
    has_promotion = fields.Boolean(required=False)
    is_featured = fields.Boolean(required=False)
    sort = fields.Str(required=False, allow_none=True)
    
    @validates('check_in')
    def validate_check_in(self, value):
        if value and value < date.today():
            raise ValidationError('Ngày nhận phòng không thể là quá khứ')
    
    @validates('check_out')
    def validate_check_out(self, value):
        if value and value < date.today():
            raise ValidationError('Ngày trả phòng không thể là quá khứ')
    
    class Meta:
        unknown = INCLUDE
class AdvancedSearchSchema(Schema):
    destination = fields.String(allow_none=True)
    check_in = fields.Date(allow_none=True)
    check_out = fields.Date(allow_none=True)
    num_guests = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    min_price = fields.Decimal(allow_none=True, as_string=False, validate=validate.Range(min=0))
    max_price = fields.Decimal(allow_none=True, as_string=False, validate=validate.Range(min=0))
    star_rating = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    amenity_ids = fields.List(fields.Integer(), allow_none=True)
    is_featured = fields.Boolean(allow_none=True)

class CheckAvailabilitySchema(Schema):
    check_in = fields.Date(required=True)
    check_out = fields.Date(required=True)
    hotel_id = fields.Integer(allow_none=True)
    room_type_id = fields.Integer(allow_none=True)
    num_guests = fields.Integer(allow_none=True, validate=validate.Range(min=1))
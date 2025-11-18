from marshmallow import Schema, fields, validate

class SearchSchema(Schema):
    destination = fields.String(allow_none=True)
    check_in = fields.Date(allow_none=True)
    check_out = fields.Date(allow_none=True)
    num_guests = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    min_price = fields.Decimal(allow_none=True, as_string=False, validate=validate.Range(min=0))
    max_price = fields.Decimal(allow_none=True, as_string=False, validate=validate.Range(min=0))
    star_rating = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))

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
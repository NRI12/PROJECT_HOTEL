from marshmallow import Schema, fields, validate, validates, ValidationError

class RoomCreateSchema(Schema):
    hotel_id = fields.Integer(required=True)
    room_type_id = fields.Integer(required=True)
    room_number = fields.String(allow_none=True)
    room_name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True)
    area = fields.Decimal(as_string=False, allow_none=True)
    max_guests = fields.Integer(required=True, validate=validate.Range(min=1))
    num_beds = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    bed_type = fields.String(allow_none=True)
    base_price = fields.Decimal(required=True, as_string=False, validate=validate.Range(min=0))
    weekend_price = fields.Decimal(as_string=False, allow_none=True, validate=validate.Range(min=0))
    quantity = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    amenity_ids = fields.List(fields.Integer(), allow_none=True)

class RoomUpdateSchema(Schema):
    room_type_id = fields.Integer()
    room_number = fields.String()
    room_name = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String()
    area = fields.Decimal(as_string=False)
    max_guests = fields.Integer(validate=validate.Range(min=1))
    num_beds = fields.Integer(validate=validate.Range(min=1))
    bed_type = fields.String()
    base_price = fields.Decimal(as_string=False, validate=validate.Range(min=0))
    weekend_price = fields.Decimal(as_string=False, validate=validate.Range(min=0))
    quantity = fields.Integer(validate=validate.Range(min=1))

class RoomAmenitySchema(Schema):
    amenity_ids = fields.List(fields.Integer(), required=True)

class RoomStatusSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf(['available', 'unavailable', 'maintenance']))

class RoomTypeCreateSchema(Schema):
    type_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(allow_none=True)

class RoomTypeUpdateSchema(Schema):
    type_name = fields.String(validate=validate.Length(min=1, max=100))
    description = fields.String(allow_none=True)

class AmenityCreateSchema(Schema):
    amenity_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    icon = fields.String(allow_none=True, validate=validate.Length(max=100))
    category = fields.String(allow_none=True, validate=validate.OneOf(['hotel', 'room', 'both']))

class AmenityUpdateSchema(Schema):
    amenity_name = fields.String(validate=validate.Length(min=1, max=100))
    icon = fields.String(allow_none=True, validate=validate.Length(max=100))
    category = fields.String(allow_none=True, validate=validate.OneOf(['hotel', 'room', 'both']))
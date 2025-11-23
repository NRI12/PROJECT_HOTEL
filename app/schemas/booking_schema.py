from marshmallow import Schema, fields, validate

class RoomBookingSchema(Schema):
    room_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))

class GuestInfoSchema(Schema):
    name = fields.String(allow_none=True)
    id_number = fields.String(allow_none=True)

class BookingCreateSchema(Schema):
    hotel_id = fields.Integer(required=True)
    check_in_date = fields.Date(required=True)
    check_out_date = fields.Date(required=True)
    num_guests = fields.Integer(required=True, validate=validate.Range(min=1))
    rooms = fields.List(fields.Nested(RoomBookingSchema), required=True)
    special_requests = fields.String(allow_none=True)
    contact_name = fields.String(allow_none=True)
    contact_phone = fields.String(allow_none=True)
    contact_email = fields.Email(allow_none=True)
    payment_method = fields.String(allow_none=True)
    discount_code = fields.String(allow_none=True)
    guests = fields.List(fields.Nested(GuestInfoSchema), allow_none=True)

class BookingUpdateSchema(Schema):
    check_in_date = fields.Date(allow_none=True)
    check_out_date = fields.Date(allow_none=True)
    num_guests = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    special_requests = fields.String(allow_none=True)

class CheckPriceSchema(Schema):
    check_in_date = fields.Date(allow_none=True)
    check_out_date = fields.Date(allow_none=True)

class BookingCancelSchema(Schema):
    reason = fields.String(allow_none=True)

class BookingValidateSchema(Schema):
    hotel_id = fields.Integer(required=True)
    check_in_date = fields.Date(required=True)
    check_out_date = fields.Date(required=True)
    num_guests = fields.Integer(required=True, validate=validate.Range(min=1))
    rooms = fields.List(fields.Nested(RoomBookingSchema), required=True)
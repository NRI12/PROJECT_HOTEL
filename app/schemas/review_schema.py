from marshmallow import Schema, fields, validate

class ReviewCreateSchema(Schema):
    booking_id = fields.Integer(required=True)
    rating = fields.Integer(required=True, validate=validate.Range(min=1, max=5))
    cleanliness_rating = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    service_rating = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    facilities_rating = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    location_rating = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    comment = fields.String(allow_none=True)

class ReviewUpdateSchema(Schema):
    rating = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    cleanliness_rating = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    service_rating = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    facilities_rating = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    location_rating = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    comment = fields.String(allow_none=True)

class ReviewResponseSchema(Schema):
    response = fields.String(required=True, validate=validate.Length(min=1))

class ReviewReportSchema(Schema):
    reason = fields.String(required=True, validate=validate.Length(min=1))
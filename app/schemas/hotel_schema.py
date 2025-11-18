from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load

class HotelCreateSchema(Schema):
    hotel_name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    description = fields.Str(allow_none=True)
    address = fields.Str(required=True, validate=validate.Length(min=5, max=500))
    city = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    district = fields.Str(allow_none=True, validate=validate.Length(max=100))
    ward = fields.Str(allow_none=True, validate=validate.Length(max=100))
    latitude = fields.Decimal(allow_none=True, places=8)
    longitude = fields.Decimal(allow_none=True, places=8)
    star_rating = fields.Int(allow_none=True, validate=validate.Range(min=1, max=5))
    phone = fields.Str(allow_none=True, validate=validate.Length(max=20))
    email = fields.Email(allow_none=True, validate=validate.Length(max=100))
    check_in_time = fields.Time(allow_none=True)
    check_out_time = fields.Time(allow_none=True)
    
    @pre_load
    def normalize_data(self, data, **kwargs):
        if 'hotel_name' in data and data['hotel_name']:
            data['hotel_name'] = data['hotel_name'].strip()
        if 'address' in data and data['address']:
            data['address'] = data['address'].strip()
        if 'city' in data and data['city']:
            data['city'] = data['city'].strip()
        return data

class HotelUpdateSchema(Schema):
    hotel_name = fields.Str(validate=validate.Length(min=2, max=200))
    description = fields.Str(allow_none=True)
    address = fields.Str(validate=validate.Length(min=5, max=500))
    city = fields.Str(validate=validate.Length(min=2, max=100))
    district = fields.Str(allow_none=True, validate=validate.Length(max=100))
    ward = fields.Str(allow_none=True, validate=validate.Length(max=100))
    latitude = fields.Decimal(allow_none=True, places=8)
    longitude = fields.Decimal(allow_none=True, places=8)
    star_rating = fields.Int(allow_none=True, validate=validate.Range(min=1, max=5))
    phone = fields.Str(allow_none=True, validate=validate.Length(max=20))
    email = fields.Email(allow_none=True, validate=validate.Length(max=100))
    check_in_time = fields.Time(allow_none=True)
    check_out_time = fields.Time(allow_none=True)
    
    @pre_load
    def normalize_data(self, data, **kwargs):
        if 'hotel_name' in data and data['hotel_name']:
            data['hotel_name'] = data['hotel_name'].strip()
        if 'address' in data and data['address']:
            data['address'] = data['address'].strip()
        if 'city' in data and data['city']:
            data['city'] = data['city'].strip()
        return data

class HotelSearchSchema(Schema):
    city = fields.Str(allow_none=True)
    min_rating = fields.Int(allow_none=True, validate=validate.Range(min=1, max=5))
    max_rating = fields.Int(allow_none=True, validate=validate.Range(min=1, max=5))
    is_featured = fields.Bool(allow_none=True)
    status = fields.Str(allow_none=True, validate=validate.OneOf(['pending', 'active', 'suspended', 'rejected']))

class AmenityUpdateSchema(Schema):
    amenity_ids = fields.List(fields.Int(), required=True)
    
    @pre_load
    def normalize_amenity_ids(self, data, **kwargs):
        """Xử lý amenity_ids từ form-data (có thể là list hoặc string)"""
        if 'amenity_ids' in data:
            value = data['amenity_ids']
            # Nếu là string (comma-separated hoặc single value), chuyển thành list
            if isinstance(value, str):
                if ',' in value:
                    data['amenity_ids'] = [int(x.strip()) for x in value.split(',') if x.strip()]
                else:
                    data['amenity_ids'] = [int(value)] if value.strip() else []
            # Nếu là list, convert các phần tử sang int
            elif isinstance(value, list):
                data['amenity_ids'] = [int(x) for x in value if str(x).strip()]
        return data

class PolicyCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    description = fields.Str(allow_none=True)
    hours_before_checkin = fields.Int(required=True, validate=validate.Range(min=0))
    refund_percentage = fields.Decimal(required=True, places=2, validate=validate.Range(min=0, max=100))
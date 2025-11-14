### app/models/hotel.py
from app import db
from datetime import datetime, time

class Hotel(db.Model):
    __tablename__ = 'hotels'
    
    hotel_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    hotel_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    district = db.Column(db.String(100))
    ward = db.Column(db.String(100))
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    star_rating = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    check_in_time = db.Column(db.Time, default=time(14, 0))
    check_out_time = db.Column(db.Time, default=time(12, 0))
    status = db.Column(db.Enum('pending', 'active', 'suspended', 'rejected'), default='pending', index=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    images = db.relationship('HotelImage', backref='hotel', lazy=True, cascade='all, delete-orphan')
    rooms = db.relationship('Room', backref='hotel', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='hotel', lazy=True)
    reviews = db.relationship('Review', backref='hotel', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='hotel', lazy=True, cascade='all, delete-orphan')
    cancellation_policies = db.relationship('CancellationPolicy', backref='hotel', lazy=True, cascade='all, delete-orphan')
    promotions = db.relationship('Promotion', backref='hotel', lazy=True, cascade='all, delete-orphan')
    amenities = db.relationship('Amenity', secondary='hotel_amenities', backref='hotels')
    
    def to_dict(self):
        return {
            'hotel_id': self.hotel_id,
            'owner_id': self.owner_id,
            'hotel_name': self.hotel_name,
            'description': self.description,
            'address': self.address,
            'city': self.city,
            'district': self.district,
            'ward': self.ward,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'star_rating': self.star_rating,
            'phone': self.phone,
            'email': self.email,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'status': self.status,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

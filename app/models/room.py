### app/models/room.py
from app import db
from datetime import datetime

class Room(db.Model):
    __tablename__ = 'rooms'
    
    room_id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.hotel_id', ondelete='CASCADE'), nullable=False, index=True)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_types.type_id'), nullable=False)
    room_number = db.Column(db.String(50))
    room_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    area = db.Column(db.Numeric(6, 2))
    max_guests = db.Column(db.Integer, nullable=False, default=2)
    num_beds = db.Column(db.Integer, default=1)
    bed_type = db.Column(db.String(100))
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    weekend_price = db.Column(db.Numeric(10, 2))
    quantity = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.Enum('available', 'unavailable', 'maintenance'), default='available')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    images = db.relationship('RoomImage', backref='room', lazy=True, cascade='all, delete-orphan')
    booking_details = db.relationship('BookingDetail', backref='room', lazy=True)
    promotions = db.relationship('Promotion', backref='room', lazy=True, cascade='all, delete-orphan')
    amenities = db.relationship('Amenity', secondary='room_amenities', backref='rooms')
    
    def to_dict(self):
        return {
            'room_id': self.room_id,
            'hotel_id': self.hotel_id,
            'room_type_id': self.room_type_id,
            'room_number': self.room_number,
            'room_name': self.room_name,
            'description': self.description,
            'area': float(self.area) if self.area else None,
            'max_guests': self.max_guests,
            'num_beds': self.num_beds,
            'bed_type': self.bed_type,
            'base_price': float(self.base_price) if self.base_price else 0,
            'weekend_price': float(self.weekend_price) if self.weekend_price else None,
            'quantity': self.quantity,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
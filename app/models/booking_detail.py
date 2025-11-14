### app/models/booking_detail.py
from app import db
from datetime import datetime

class BookingDetail(db.Model):
    __tablename__ = 'booking_details'
    
    detail_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.booking_id', ondelete='CASCADE'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_per_night = db.Column(db.Numeric(10, 2), nullable=False)
    num_nights = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'detail_id': self.detail_id,
            'booking_id': self.booking_id,
            'room_id': self.room_id,
            'quantity': self.quantity,
            'price_per_night': float(self.price_per_night) if self.price_per_night else 0,
            'num_nights': self.num_nights,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

### app/models/booking.py
from app import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    booking_id = db.Column(db.Integer, primary_key=True)
    booking_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.hotel_id'), nullable=False, index=True)
    check_in_date = db.Column(db.Date, nullable=False, index=True)
    check_out_date = db.Column(db.Date, nullable=False, index=True)
    num_guests = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    final_amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.Enum('pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled', 'refunded'), default='confirmed', index=True)
    payment_status = db.Column(db.Enum('unpaid', 'partial', 'paid', 'refunded'), default='unpaid')
    special_requests = db.Column(db.Text)
    cancellation_reason = db.Column(db.Text)
    cancelled_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    booking_details = db.relationship('BookingDetail', backref='booking', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='booking', lazy=True)
    reviews = db.relationship('Review', backref='booking', lazy=True)
    discount_usage = db.relationship('DiscountUsage', backref='booking', lazy=True)
    
    def to_dict(self):
        return {
            'booking_id': self.booking_id,
            'booking_code': self.booking_code,
            'user_id': self.user_id,
            'hotel_id': self.hotel_id,
            'check_in_date': self.check_in_date.isoformat() if self.check_in_date else None,
            'check_out_date': self.check_out_date.isoformat() if self.check_out_date else None,
            'num_guests': self.num_guests,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'final_amount': float(self.final_amount) if self.final_amount else 0,
            'status': self.status,
            'payment_status': self.payment_status,
            'special_requests': self.special_requests,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

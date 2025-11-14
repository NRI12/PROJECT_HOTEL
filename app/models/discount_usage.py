### app/models/discount_usage.py
from app import db
from datetime import datetime

class DiscountUsage(db.Model):
    __tablename__ = 'discount_usage'
    
    usage_id = db.Column(db.Integer, primary_key=True)
    code_id = db.Column(db.Integer, db.ForeignKey('discount_codes.code_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.booking_id'), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'usage_id': self.usage_id,
            'code_id': self.code_id,
            'user_id': self.user_id,
            'booking_id': self.booking_id,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'used_at': self.used_at.isoformat() if self.used_at else None
        }

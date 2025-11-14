### app/models/promotion.py
from app import db
from datetime import datetime

class Promotion(db.Model):
    __tablename__ = 'promotions'
    
    promotion_id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.hotel_id', ondelete='CASCADE'))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id', ondelete='CASCADE'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    discount_type = db.Column(db.Enum('percentage', 'fixed'), nullable=False)
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, index=True)
    end_date = db.Column(db.DateTime, nullable=False, index=True)
    applicable_days = db.Column(db.String(50))
    min_nights = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'promotion_id': self.promotion_id,
            'hotel_id': self.hotel_id,
            'room_id': self.room_id,
            'title': self.title,
            'description': self.description,
            'discount_type': self.discount_type,
            'discount_value': float(self.discount_value) if self.discount_value else 0,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'applicable_days': self.applicable_days,
            'min_nights': self.min_nights,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

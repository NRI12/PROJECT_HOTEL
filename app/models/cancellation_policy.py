### app/models/cancellation_policy.py
from app import db
from datetime import datetime

class CancellationPolicy(db.Model):
    __tablename__ = 'cancellation_policies'
    
    policy_id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.hotel_id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    hours_before_checkin = db.Column(db.Integer, nullable=False)
    refund_percentage = db.Column(db.Numeric(5, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'policy_id': self.policy_id,
            'hotel_id': self.hotel_id,
            'name': self.name,
            'description': self.description,
            'hours_before_checkin': self.hours_before_checkin,
            'refund_percentage': float(self.refund_percentage) if self.refund_percentage else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


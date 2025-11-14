### app/models/review.py
from app import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'reviews'
    
    review_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.booking_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.hotel_id', ondelete='CASCADE'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    cleanliness_rating = db.Column(db.Integer)
    service_rating = db.Column(db.Integer)
    facilities_rating = db.Column(db.Integer)
    location_rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    hotel_response = db.Column(db.Text)
    response_date = db.Column(db.DateTime)
    is_reported = db.Column(db.Boolean, default=False)
    report_reason = db.Column(db.Text)
    status = db.Column(db.Enum('active', 'hidden', 'removed'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('booking_id', name='unique_booking_review'),)
    
    def to_dict(self):
        return {
            'review_id': self.review_id,
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'hotel_id': self.hotel_id,
            'rating': self.rating,
            'cleanliness_rating': self.cleanliness_rating,
            'service_rating': self.service_rating,
            'facilities_rating': self.facilities_rating,
            'location_rating': self.location_rating,
            'comment': self.comment,
            'hotel_response': self.hotel_response,
            'response_date': self.response_date.isoformat() if self.response_date else None,
            'is_reported': self.is_reported,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

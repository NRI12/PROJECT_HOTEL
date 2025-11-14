### app/models/favorite.py
from app import db
from datetime import datetime

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    favorite_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.hotel_id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'hotel_id', name='unique_favorite'),)
    
    def to_dict(self):
        return {
            'favorite_id': self.favorite_id,
            'user_id': self.user_id,
            'hotel_id': self.hotel_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

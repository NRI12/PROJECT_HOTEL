### app/models/room_image.py
from app import db
from datetime import datetime

class RoomImage(db.Model):
    __tablename__ = 'room_images'
    
    image_id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    caption = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'image_id': self.image_id,
            'room_id': self.room_id,
            'image_url': self.image_url,
            'is_primary': self.is_primary,
            'caption': self.caption,
            'display_order': self.display_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


### app/models/amenity.py
from app import db
from datetime import datetime

class Amenity(db.Model):
    __tablename__ = 'amenities'
    
    amenity_id = db.Column(db.Integer, primary_key=True)
    amenity_name = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(100))
    category = db.Column(db.Enum('hotel', 'room', 'both'), default='both')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'amenity_id': self.amenity_id,
            'amenity_name': self.amenity_name,
            'icon': self.icon,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


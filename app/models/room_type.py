### app/models/room_type.py
from app import db
from datetime import datetime

class RoomType(db.Model):
    __tablename__ = 'room_types'
    
    type_id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    rooms = db.relationship('Room', backref='room_type', lazy=True)
    
    def to_dict(self):
        return {
            'type_id': self.type_id,
            'type_name': self.type_name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
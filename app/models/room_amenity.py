### app/models/room_amenity.py
from app import db

room_amenities = db.Table('room_amenities',
    db.Column('room_id', db.Integer, db.ForeignKey('rooms.room_id', ondelete='CASCADE'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenities.amenity_id', ondelete='CASCADE'), primary_key=True)
)

### app/models/hotel_amenity.py
from app import db

hotel_amenities = db.Table('hotel_amenities',
    db.Column('hotel_id', db.Integer, db.ForeignKey('hotels.hotel_id', ondelete='CASCADE'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenities.amenity_id', ondelete='CASCADE'), primary_key=True)
)
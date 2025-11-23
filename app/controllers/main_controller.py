from flask import request, session
from app import db
from app.models.hotel import Hotel
from app.models.room import Room
from app.models.review import Review
from app.models.promotion import Promotion
from app.models.amenity import Amenity
from sqlalchemy import func
from datetime import datetime

class MainController:
    
    @staticmethod
    def get_home_data():
        try:
            featured_hotels = Hotel.query.filter_by(status='active', is_featured=True).limit(6).all()
            
            hotels_data = []
            for hotel in featured_hotels:
                min_price = db.session.query(func.min(Room.base_price))\
                    .filter(Room.hotel_id == hotel.hotel_id)\
                    .filter(Room.status == 'available')\
                    .scalar() or 1000000
                
                review_count = Review.query.filter_by(hotel_id=hotel.hotel_id, status='active').count()
                
                avg_rating = db.session.query(func.avg(Review.rating))\
                    .filter_by(hotel_id=hotel.hotel_id, status='active')\
                    .scalar() or 4.0
                
                hotels_data.append({
                    'hotel': hotel,
                    'min_price': int(min_price),
                    'review_count': review_count,
                    'avg_rating': float(avg_rating) if avg_rating else 4.0
                })
            
            cities = db.session.query(
                Hotel.city,
                func.count(Hotel.hotel_id).label('hotel_count')
            ).filter_by(status='active')\
            .group_by(Hotel.city)\
            .order_by(func.count(Hotel.hotel_id).desc())\
            .limit(6).all()
            
            popular_cities = []
            for city_name, count in cities:
                sample_hotel = Hotel.query.filter_by(city=city_name, status='active').first()
                popular_cities.append({
                    'name': city_name,
                    'count': count,
                    'image': sample_hotel.images[0].image_url if sample_hotel and sample_hotel.images else None
                })
            
            active_promotions = Promotion.query.filter(
                Promotion.start_date <= datetime.utcnow(),
                Promotion.end_date >= datetime.utcnow(),
                Promotion.is_active == True
            ).limit(2).all()
            
            return {
                'featured_hotels': hotels_data,
                'popular_cities': popular_cities,
                'active_promotions': active_promotions
            }
            
        except Exception as e:
            print(f'Lỗi lấy dữ liệu trang chủ: {str(e)}')
            return {
                'featured_hotels': [],
                'popular_cities': [],
                'active_promotions': []
            }
    
    @staticmethod
    def get_search_suggestions(query_text):
        try:
            if not query_text:
                return {'suggestions': []}
            
            cities = db.session.query(Hotel.city).filter(
                Hotel.city.ilike(f'%{query_text}%'),
                Hotel.status == 'active'
            ).distinct().limit(5).all()
            
            hotels = Hotel.query.filter(
                Hotel.hotel_name.ilike(f'%{query_text}%'),
                Hotel.status == 'active'
            ).limit(5).all()
            
            suggestions = []
            for city in cities:
                suggestions.append({'type': 'city', 'value': city[0]})
            
            for hotel in hotels:
                suggestions.append({
                    'type': 'hotel', 
                    'value': hotel.hotel_name, 
                    'id': hotel.hotel_id,
                    'city': hotel.city
                })
            
            return {'suggestions': suggestions}
            
        except Exception as e:
            print(f'Lỗi lấy gợi ý: {str(e)}')
            return {'suggestions': []}
    
    @staticmethod
    def get_all_amenities():
        try:
            return Amenity.query.all()
        except Exception as e:
            print(f'Lỗi lấy amenities: {str(e)}')
            return []


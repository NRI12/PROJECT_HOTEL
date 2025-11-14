### app/models/search_history.py
from app import db
from datetime import datetime

class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    
    search_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    destination = db.Column(db.String(200))
    check_in_date = db.Column(db.Date)
    check_out_date = db.Column(db.Date)
    num_guests = db.Column(db.Integer)
    search_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'search_id': self.search_id,
            'user_id': self.user_id,
            'destination': self.destination,
            'check_in_date': self.check_in_date.isoformat() if self.check_in_date else None,
            'check_out_date': self.check_out_date.isoformat() if self.check_out_date else None,
            'num_guests': self.num_guests,
            'search_date': self.search_date.isoformat() if self.search_date else None
        }

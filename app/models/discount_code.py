### app/models/discount_code.py
from app import db
from datetime import datetime

class DiscountCode(db.Model):
    __tablename__ = 'discount_codes'
    
    code_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    code = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text)
    discount_type = db.Column(db.Enum('percentage', 'fixed'), nullable=False)
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    min_order_amount = db.Column(db.Numeric(10, 2), default=0)
    max_discount_amount = db.Column(db.Numeric(10, 2))
    usage_limit = db.Column(db.Integer)
    used_count = db.Column(db.Integer, default=0)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = db.relationship('User', backref='discount_codes', lazy=True)
    discount_usage = db.relationship('DiscountUsage', backref='discount_code', lazy=True)
    
    # Add unique constraint for code per owner
    __table_args__ = (
        db.UniqueConstraint('owner_id', 'code', name='uq_owner_code'),
    )
    
    def to_dict(self):
        return {
            'code_id': self.code_id,
            'owner_id': self.owner_id,
            'code': self.code,
            'description': self.description,
            'discount_type': self.discount_type,
            'discount_value': float(self.discount_value) if self.discount_value else 0,
            'min_order_amount': float(self.min_order_amount) if self.min_order_amount else 0,
            'max_discount_amount': float(self.max_discount_amount) if self.max_discount_amount else None,
            'usage_limit': self.usage_limit,
            'used_count': self.used_count,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
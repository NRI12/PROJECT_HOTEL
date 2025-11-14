### app/models/payment.py
from app import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    
    payment_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.booking_id'), nullable=False, index=True)
    payment_method = db.Column(db.Enum('credit_card', 'bank_transfer', 'momo', 'zalopay', 'vnpay', 'cash'), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    transaction_id = db.Column(db.String(100))
    payment_status = db.Column(db.Enum('pending', 'completed', 'failed', 'refunded'), default='pending')
    payment_date = db.Column(db.DateTime)
    refund_amount = db.Column(db.Numeric(10, 2), default=0)
    refund_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'payment_id': self.payment_id,
            'booking_id': self.booking_id,
            'payment_method': self.payment_method,
            'amount': float(self.amount) if self.amount else 0,
            'transaction_id': self.transaction_id,
            'payment_status': self.payment_status,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'refund_amount': float(self.refund_amount) if self.refund_amount else 0,
            'refund_date': self.refund_date.isoformat() if self.refund_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


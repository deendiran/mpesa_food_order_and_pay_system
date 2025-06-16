# models/payment.py
from models import db
from sqlalchemy.sql import func

class Payment(db.Model):
    __tablename__ = "payments"
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    amount = db.Column(db.DECIMAL(10, 2), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    transaction_id = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    status = db.Column(db.String(20), default="pending")
    mpesa_receipt_number = db.Column(db.String(100))
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    order = db.relationship("Order", back_populates="payments")
    push_requests = db.relationship('PushRequest', back_populates='payment', cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'phone_number': self.phone_number,
            'status': self.status,
            'mpesa_receipt_number': self.mpesa_receipt_number,
            'error_message': self.error_message,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class PushRequest(db.Model):
    __tablename__ = "push_requests"

    id = db.Column(db.Integer, primary_key=True)
    payments_id = db.Column(
        db.Integer,
        db.ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
    )
    checkout_request_id = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now()
    )

    # Relationship with Payment model
    payment = db.relationship("Payment", back_populates="push_requests")

    def to_dict(self):
        return {
            "id": self.id,
            "payments_id": self.payments_id,
            "checkout_request_id": self.checkout_request_id,
            "date_created": self.date_created.isoformat()
            if self.date_created
            else None,
            "last_updated": self.last_updated.isoformat()
            if self.last_updated
            else None,
        }
# models/order.py
from models import db
from sqlalchemy.sql import func

class Order(db.Model):
    __tablename__ = "orders"
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    total_amount = db.Column(db.DECIMAL(10, 2), nullable=False)
    status = db.Column(db.String(20), default="pending", index=True)
    payment_status = db.Column(db.String(20), default="pending", index=True)
    payment_method = db.Column(db.String(20), default="mpesa")
    mpesa_transaction_id = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20), nullable=False)
    delivery_address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    # Relationships with proper cascade deletions
    user = db.relationship("User", back_populates="orders")
    order_items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = db.relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    status_history = db.relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount) if self.total_amount else 0.0,
            'status': self.status,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'customer_phone': self.customer_phone,
            'mpesa_transaction_id': self.mpesa_transaction_id,
            'delivery_address': self.delivery_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class OrderItem(db.Model):
    __tablename__ = "order_items"
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    subtotal = db.Column(db.DECIMAL(10, 2), nullable=False)
    
    # Relationships
    order = db.relationship("Order", back_populates="order_items")
    menu_item = db.relationship("MenuItem", back_populates="order_items")
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'menu_item_id': self.menu_item_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'subtotal': self.subtotal
        }

class OrderStatusHistory(db.Model):
    __tablename__ = "order_status_history"
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    
    # Relationships
    order = db.relationship("Order", back_populates="status_history")
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'created_at': self.created_at
        }
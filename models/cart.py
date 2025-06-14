# models/cart.py
from . import db
from sqlalchemy.sql import func

class CartItem(db.Model):
    __tablename__ = "cart_items"
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=func.now())
    
    # Relationships
    user = db.relationship("User", back_populates="cart_items")
    menu_item = db.relationship("MenuItem", back_populates="cart_items")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'menu_item_id': self.menu_item_id,
            'quantity': self.quantity,
            'created_at': self.created_at
        }
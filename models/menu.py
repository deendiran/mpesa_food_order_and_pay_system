# models/menu.py
from models import db

class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    is_available = db.Column(db.Boolean, default=True)

    # Relationships
    category = db.relationship("Category", back_populates="menu_items")
    order_items = db.relationship("OrderItem", back_populates="menu_item")
    cart_items = db.relationship("CartItem", back_populates="menu_item")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'category_id': self.category_id,
            'is_available': self.is_available
        }
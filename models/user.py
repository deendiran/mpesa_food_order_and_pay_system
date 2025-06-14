# models/user.py
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from . import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    contacts = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    last_login = db.Column(db.DateTime)  

    # Relationships
    orders = db.relationship("Order", back_populates="user")
    cart_items = db.relationship("CartItem", back_populates="user")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_login_time(self):
        self.last_login = datetime.now()
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'fullname': self.fullname,
            'contact': self.contacts,
            'email': self.email,
            'password': self.password_hash
        }
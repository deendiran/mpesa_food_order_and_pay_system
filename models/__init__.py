from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
from datetime import datetime

db = SQLAlchemy()

# Import all models to make them available when importing from models
from .user import User
from .menu import MenuItem
from .category import Category
from .order import Order, OrderItem, OrderStatusHistory
from .payment import Payment
from .cart import CartItem

__all__ = ['db', 'User', 'Category', 'MenuItem', 'Order', 'OrderItem', 
           'Payment', 'CartItem', 'OrderStatusHistory']
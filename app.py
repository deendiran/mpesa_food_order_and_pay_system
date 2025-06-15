# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from models import db

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure SQLite database 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nourish_net.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = '2898db2a80a4f110e39490e2de8425c8c2523045587c08f1'

# Configure session cookie
app.config['SESSION_COOKIE_NAME'] = 'nourish_net_session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# M-Pesa configuration
app.config["MPESA_BASE_URL"] = "https://sandbox.safaricom.co.ke"
app.config["MPESA_ACCESS_TOKEN_URL"] = "/oauth/v1/generate?grant_type=client_credentials"
app.config["MPESA_STK_PUSH_URL"] = "/mpesa/stkpush/v1/processrequest"
app.config["MPESA_STK_QUERY_URL"] = "/mpesa/stkpushquery/v1/query"
app.config["MPESA_CONSUMER_KEY"] = "sB2Gdv6pqxdDD62uxZhsWS3f0hM01EPGdpw6cDwgdypAOZOw"
app.config["MPESA_CONSUMER_SECRET"] = "ETPTjx8zZZKl7Mce4QsGJkMLWLJX8TYx8HxrY5qadqQFVAXy5GAEovL5tsbCCGtN"
app.config["MPESA_PASSKEY"] = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
app.config["MPESA_TILL_NUMBER"] = "174379"
app.config["MPESA_BUSINESS_SHORT_CODE"] = "174379"
app.config["MPESA_CALLBACK_URL"] = "https://d864-41-90-172-126.ngrok-free.app/callback"

# Initialize db with app
db.init_app(app)

# Import models after db initialization
with app.app_context():
    from models.user import User
    from models.category import Category
    from models.menu import MenuItem
    from models.order import Order, OrderItem, OrderStatusHistory
    from models.payment import Payment, PushRequest
    from models.cart import CartItem

# Import routes after models are defined
from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
"""
routes.py - Main application routes for the Food Ordering System

This file contains all the route definitions for:
- User authentication (register, login, logout)
- Menu and category management
- Order processing
- M-Pesa payment integration
- Error handling

The application uses Flask for routing and SQLAlchemy for database operations.
"""

from flask import render_template, request, jsonify, session, current_app, redirect, url_for
from datetime import datetime, timedelta
import base64
import requests
import json
import os
from sqlalchemy.sql import func
from app import app
from models import db
from models.user import User
from models.category import Category
from models.menu import MenuItem
from models.order import Order, OrderItem, OrderStatusHistory
from models.payment import Payment, PushRequest
from models.cart import CartItem
from werkzeug.security import generate_password_hash, check_password_hash

# ==================================================================
# HELPER FUNCTIONS
# ==================================================================

def validate_user_data(data, is_login=False):
    """
    Validates user registration/login data
    
    Args:
        data (dict): User data to validate
        is_login (bool): Whether validating for login (skip uniqueness checks)
    
    Returns:
        tuple: (bool success, str message)
    """
    if is_login:
        # Login validation - just check required fields
        if not data.get('contact') or not data.get('password'):
            return False, "Phone and password are required"
    else:
        # Registration validation - more comprehensive checks
        required = ['fullname', 'email', 'contact', 'password']
        if not all(k in data for k in required):
            return False, "All fields are required"
        
        # Check for existing email
        if User.query.filter_by(email=data['email']).first():
            return False, "Email already registered"
        
        # Check for existing phone number
        if User.query.filter_by(contacts=data['contact']).first():
            return False, "Phone number already registered"
    
    return True, ""

def get_access_token():
    """
    Gets an access token from the Safaricom M-Pesa API
    
    Returns:
        str: Access token or None if failed
    """
    try:
        # Construct the full URL from config
        base_url = current_app.config["MPESA_BASE_URL"].rstrip('/')
        token_url = current_app.config["MPESA_ACCESS_TOKEN_URL"].lstrip('/')
        url = f"{base_url}/{token_url}"
        
        # Set up authentication headers
        headers = {"Content-Type": "application/json"}
        auth = (
            current_app.config["MPESA_CONSUMER_KEY"],
            current_app.config["MPESA_CONSUMER_SECRET"]
        )

        # Make the API request
        response = requests.get(
            url, 
            headers=headers, 
            auth=auth, 
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        
        if 'access_token' in result:
            current_app.logger.info("Successfully obtained M-Pesa access token")
            return result['access_token']
        else:
            error_msg = result.get('errorMessage', 'Unknown error')
            current_app.logger.error(f"M-Pesa token error: {error_msg}")
            return None

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error getting M-Pesa access token: {str(e)}")
        current_app.logger.error(f"Request URL: {url}")
        current_app.logger.error(f"Auth: {auth}")
        return None

def format_phone_number(phone_number):
    """
    Formats phone numbers to M-Pesa compatible format (254XXXXXXXXX)
    
    Args:
        phone_number (str): Raw phone number input
        
    Returns:
        str: Formatted phone number
    """
    # Remove any non-digit characters
    phone_number = "".join(filter(str.isdigit, phone_number))
    
    # Handle different input formats:
    if phone_number.startswith("254") and len(phone_number) == 12:
        return phone_number  # Already correct format
    elif phone_number.startswith("0") and len(phone_number) == 10:
        # Convert 07... or 01... to 2547... or 2541...
        return "254" + phone_number[1:]
    elif phone_number.startswith("7") or phone_number.startswith("1") and len(phone_number) == 9:
        # Convert 7... or 1... to 2547... or 2541...
        return "254" + phone_number
    elif phone_number.startswith("+254") and len(phone_number) == 13:
        return phone_number[1:]  # Remove the +
    
    # If none of the above, return as is (will fail validation)
    return phone_number

# ==================================================================
# AUTHENTICATION ROUTES
# ==================================================================

@app.route("/")
@app.route("/<page>")
def index(page=None):
    """Serves the main frontend application"""
    return render_template("index.html")

@app.route("/login")
@app.route("/register")
def auth_pages():
    """Serves authentication pages (handled by frontend routing)"""
    return render_template("index.html")

@app.route("/api/register", methods=["POST"])
def register():
    """
    Handles user registration
    
    Expected JSON:
    {
        "fullname": "User Name",
        "email": "user@example.com",
        "contact": "0712345678",
        "password": "securepassword"
    }
    """
    data = request.get_json()

    # Validate input data
    valid, message = validate_user_data(data)
    if not valid:
        return jsonify({"success": False, "message": message}), 400

    try:
        # Create new user
        user = User(
            fullname=data["fullname"], 
            email=data["email"], 
            contacts=data["contact"]
        )
        user.set_password(data["password"])

        # Save to database
        db.session.add(user)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Registration successful",
            "user": {
                "id": user.id,
                "fullname": user.fullname,
                "email": user.email,
                "contact": user.contacts,
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/login", methods=["POST"])
def login():
    """
    Handles user login
    
    Expected JSON:
    {
        "contact": "0712345678",
        "password": "userpassword"
    }
    """
    data = request.get_json()

    # Validate input
    valid, message = validate_user_data(data, is_login=True)
    if not valid:
        return jsonify({"success": False, "message": message}), 400

    try:
        # Find user by phone number
        user = User.query.filter_by(contacts=data["contact"]).first()

        # Verify password
        if user and user.check_password(data["password"]):
            # Create session
            session["user_id"] = user.id
            session.permanent = True

            # Update last login time
            user.last_login = datetime.now()
            db.session.commit()

            return jsonify({
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "fullname": user.fullname,
                    "email": user.email,
                    "contact": user.contacts,
                }
            })
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/check-session", methods=["GET"])
def check_session():
    """Checks if user has a valid session"""
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user:
            return jsonify({"valid": True, "user": user.to_dict()})
    return jsonify({"valid": False})

@app.before_request
def check_valid_session():
    """
    Global session checker - runs before each request
    Skips authentication for static files and auth routes
    """
    if request.path.startswith("/static/") or request.path in [
        "/api/login",
        "/api/register",
        "/",
    ]:
        return

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

@app.route("/api/user", methods=["GET"])
def get_user_info():
    """Gets current user's information"""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"success": False, "message": "User not logged in"}), 404

    return jsonify({
        "success": True,
        "user": {
            "id": user.id,
            "fullname": user.fullname,
            "email": user.email,
            "contact": user.contacts,
        }
    })

@app.route("/api/logout", methods=["POST"])
def logout():
    """Terminates the current session"""
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})

# ==================================================================
# MENU & CATEGORY ROUTES
# ==================================================================

@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Gets all active food categories"""
    categories = Category.query.filter_by(is_active=True).all()
    return jsonify([category.to_dict() for category in categories])

@app.route("/api/menu/category/<int:category_id>", methods=["GET"])
def get_menu_by_category(category_id):
    """Gets menu items for a specific category"""
    # Verify category exists
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"success": False, "message": "Category not found"}), 404

    # Get available items in category
    menu_items = MenuItem.query.filter_by(
        category_id=category_id, is_available=True
    ).all()

    return jsonify([item.to_dict() for item in menu_items])

@app.route("/api/menu", methods=["GET"])
def get_menu():
    """Gets all available menu items"""
    menu_items = MenuItem.query.filter_by(is_available=True).all()
    return jsonify([item.to_dict() for item in menu_items])

@app.route("/api/menu/<int:item_id>", methods=["GET"])
def get_menu_item(item_id):
    """Gets details for a specific menu item"""
    menu_item = MenuItem.query.get(item_id)
    if not menu_item:
        return jsonify({"success": False, "message": "Menu item not found"}), 404
    return jsonify({"success": True, "item": menu_item.to_dict()})

# ==================================================================
# ORDER MANAGEMENT ROUTES
# ==================================================================

@app.route("/api/orders", methods=["POST"])
def create_order():
    """
    Creates a new order
    
    Expected JSON:
    {
        "total_amount": 1500.00,
        "customer_phone": "0712345678",
        "items": [
            {
                "menu_item_id": 1,
                "quantity": 2,
                "unit_price": 500.00,
                "subtotal": 1000.00
            },
            ...
        ]
    }
    """
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json()

    # Check if updating existing order
    if "order_id" in data and data["order_id"]:
        return update_order(data["order_id"])

    try:
        # Create new order
        order = Order(
            user_id=session["user_id"],
            total_amount=data["total_amount"],
            customer_phone=data["customer_phone"],
            status=data.get("status", "pending"),
            payment_status=data.get("payment_status", "pending"),
        )

        db.session.add(order)
        db.session.commit()

        # Add order items
        for item in data["items"]:
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item["menu_item_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                subtotal=item["subtotal"],
            )
            db.session.add(order_item)

        db.session.commit()

        return jsonify({
            "success": True,
            "order_id": order.id,
            "message": "Order created successfully"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/orders', methods=['GET'])
def get_user_orders():
    """Gets all orders for the current user with detailed items"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        # Get orders with related data using joinedload for performance
        orders = Order.query.filter_by(user_id=session['user_id']).options(
            db.joinedload(Order.order_items).joinedload(OrderItem.menu_item)
        ).all()
        
        # Format response data
        orders_list = []
        for order in orders:
            order_data = order.to_dict()
            order_data['items'] = []
            
            for item in order.order_items:
                item_data = {
                    'id': item.id,
                    'name': item.menu_item.name if item.menu_item else 'Deleted Item',
                    'menu_item_id': item.menu_item_id,
                    'quantity': item.quantity,
                    'price': float(item.unit_price) if item.unit_price else 0.0,
                    'subtotal': float(item.subtotal) if item.subtotal else 0.0
                }
                order_data['items'].append(item_data)
            
            orders_list.append(order_data)
        
        return jsonify(orders_list)
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route("/api/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    """Gets details for a specific order"""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    order = Order.query.filter_by(id=order_id, user_id=session["user_id"]).first()

    if not order:
        return jsonify({"success": False, "message": "Order not found"}), 404

    return jsonify({
        'success': True,
        'order': order.to_dict()
    })

@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Deletes an order and all related records"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        # Delete related records first (maintain referential integrity)
        OrderItem.query.filter_by(order_id=order_id).delete()
        OrderStatusHistory.query.filter_by(order_id=order_id).delete()
        
        # Then delete the order
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({'success': True}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route("/api/orders/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    """
    Updates an order's status
    
    Expected JSON:
    {
        "status": "confirmed|cancelled|completed"
    }
    """
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json()
    if not data or "status" not in data:
        return jsonify({"success": False, "message": "Status is required"}), 400

    try:
        # Get and verify order belongs to user
        order = Order.query.filter_by(id=order_id, user_id=session["user_id"]).first()

        if not order:
            return jsonify({"success": False, "message": "Order not found"}), 404

        # Create status history record
        status_history = OrderStatusHistory(
            order_id=order.id, 
            old_status=order.status, 
            new_status=data["status"]
        )
        db.session.add(status_history)

        # Update order status
        order.status = data["status"]
        db.session.commit()

        return jsonify({"success": True, "order": order.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    """
    Updates an existing order
    
    Expected JSON:
    {
        "total_amount": 1500.00,
        "customer_phone": "0712345678",
        "status": "pending",
        "payment_status": "pending",
        "items": [
            {
                "menu_item_id": 1,
                "quantity": 2,
                "unit_price": 500.00,
                "subtotal": 1000.00
            },
            ...
        ]
    }
    """
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json()

    try:
        # Get and verify order
        order = Order.query.filter_by(id=order_id, user_id=session["user_id"]).first()

        if not order:
            return jsonify({"success": False, "message": "Order not found"}), 404

        # Validate total amount
        if "total_amount" not in data or data["total_amount"] is None:
            return jsonify({"success": False, "message": "Total amount is required"}), 400

        # Update order fields
        order.total_amount = float(data["total_amount"])
        order.status = data.get("status", order.status)
        order.payment_status = data.get("payment_status", order.payment_status)
        order.customer_phone = data.get("customer_phone", order.customer_phone)
        order.updated_at = func.now()

        # Clear existing items
        OrderItem.query.filter_by(order_id=order.id).delete()

        # Add new items
        for item in data["items"]:
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item["menu_item_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                subtotal=item["subtotal"],
            )
            db.session.add(order_item)

        db.session.commit()

        return jsonify({"success": True, "order_id": order.id})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# ==================================================================
# PAYMENT PROCESSING ROUTES
# ==================================================================

@app.route("/api/make-payment", methods=["POST"])
def make_payment():
    """
    Initiates M-Pesa STK push payment
    
    Expected JSON:
    {
        "phone": "0712345678",
        "amount": 1500,
        "order_id": 123
    }
    """
    data = request.get_json()

    # Validate input
    required_fields = ["phone", "amount", "order_id"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # 1. Get M-Pesa access token
        access_token = get_access_token()
        if not access_token:
            return jsonify({"error": "Failed to get access token"}), 500

        # 2. Format phone number
        phone = format_phone_number(data["phone"])
        if not phone.startswith("254") or len(phone) != 12:
            return jsonify({"error": "Invalid phone format"}), 400

        # 3. Create timestamp and password
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        passkey = current_app.config["MPESA_PASSKEY"]
        business_short_code = current_app.config["MPESA_BUSINESS_SHORT_CODE"]
        password = base64.b64encode(
            f"{business_short_code}{passkey}{timestamp}".encode()
        ).decode()

        # 4. Prepare STK push request
        stk_push_url = (
            f"{current_app.config['MPESA_BASE_URL']}/mpesa/stkpush/v1/processrequest"
        )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "BusinessShortCode": business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(data["amount"]),
            "PartyA": phone,
            "PartyB": business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": current_app.config["MPESA_CALLBACK_URL"],
            "AccountReference": f"Order{data['order_id']}",
            "TransactionDesc": "Food Order Payment",
        }

        # 5. Make the API request
        response = requests.post(stk_push_url, json=payload, headers=headers)
        response_data = response.json()

        # 6. Handle response
        if response.status_code == 200 and "ResponseCode" in response_data:
            if response_data["ResponseCode"] == "0":
                return jsonify({
                    "success": True,
                    "message": "Payment initiated",
                    "checkout_request_id": response_data["CheckoutRequestID"],
                })

        # If we get here, something went wrong
        return jsonify({
            "success": False,
            "error": "STK push failed",
            "mpesa_response": response_data,
            "status_code": response.status_code,
        }), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/test-payment")
def test_payment():
    """Test endpoint for payment processing"""
    test_data = {
        "phone": "254114505949",  # Sandbox test number
        "amount": 1,  # 1 KSH
        "order_id": 123,
    }
    return make_payment(test_data)

@app.route("/api/query-payment-status", methods=["POST"])
def perform_stk_query():
    """
    Queries M-Pesa for payment status
    
    Expected JSON:
    {
        "checkout_request_id": "ws_CO_123456789"
    }
    """
    data = request.get_json()
    checkout_request_id = data.get("checkout_request_id")

    if not checkout_request_id:
        return jsonify({"error": "Checkout Request ID not provided"}), 400

    try:
        # Get access token
        access_token = get_access_token()
        if not access_token:
            return jsonify({"error": "Failed to get M-Pesa access token"}), 500

        # Prepare query parameters
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            (
                current_app.config["MPESA_BUSINESS_SHORT_CODE"]
                + current_app.config["MPESA_PASSKEY"]
                + timestamp
            ).encode()
        ).decode()

        query_url = os.path.join(
            current_app.config["MPESA_BASE_URL"],
            current_app.config["MPESA_STK_QUERY_URL"],
        )

        query_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
        }

        query_payload = {
            "BusinessShortCode": current_app.config["MPESA_BUSINESS_SHORT_CODE"],
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id,
        }

        # Send query request
        response = requests.post(query_url, headers=query_headers, json=query_payload)
        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/check-payment-status/<checkout_request_id>")
def check_status(checkout_request_id):
    """Alternative endpoint for checking payment status"""
    access_token = get_access_token()
    if not access_token:
        return jsonify({"error": "No token"}), 500

    url = f"{current_app.config['MPESA_BASE_URL']}/mpesa/stkpushquery/v1/query"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "BusinessShortCode": current_app.config["MPESA_BUSINESS_SHORT_CODE"],
        "Password": base64.b64encode(
            f"{current_app.config['MPESA_BUSINESS_SHORT_CODE']}{current_app.config['MPESA_PASSKEY']}{datetime.now().strftime('%Y%m%d%H%M%S')}".encode()
        ).decode(),
        "Timestamp": datetime.now().strftime("%Y%m%d%H%M%S"),
        "CheckoutRequestID": checkout_request_id,
    }

    response = requests.post(url, json=payload, headers=headers)
    return jsonify(response.json())

@app.route("/test-mpesa-token")
def test_mpesa_token():
    """Tests M-Pesa token generation"""
    token = get_access_token()
    if token:
        return jsonify({"success": True, "token": token})
    return jsonify({"success": False, "error": "Failed to get token"})

@app.route("/api/mpesa-callback", methods=["GET"])
def callback_verification():
    """Required for M-Pesa URL verification"""
    return jsonify({"status": "ok"}), 200

@app.route("/api/mpesa-callback", methods=["POST"])
def mpesa_callback():
    """
    Handles M-Pesa payment callback notifications
    This is where payment confirmations are processed
    """
    try:
        current_app.logger.info("Raw MPESA callback data: %s", request.data)
        data = request.get_json()

        if not data:
            current_app.logger.error("No data received in callback")
            return jsonify({"success": False, "message": "No data received"}), 400

        # Extract callback data
        callback_data = data.get("Body", {}).get("stkCallback", {})
        current_app.logger.info("Callback data: %s", callback_data)

        if not callback_data:
            current_app.logger.error("Invalid callback data structure")
            return jsonify({"success": False, "message": "Invalid callback data"}), 400

        result_code = callback_data.get("ResultCode")
        checkout_request_id = callback_data.get("CheckoutRequestID")
        current_app.logger.info(
            "ResultCode: %s, CheckoutRequestID: %s", result_code, checkout_request_id
        )

        result_desc = callback_data.get("ResultDesc")
        callback_metadata = callback_data.get("CallbackMetadata", {}).get("Item", [])

        # Find the payment record
        push_request = PushRequest.query.filter_by(
            checkout_request_id=checkout_request_id
        ).first()

        if not push_request:
            current_app.logger.error(
                "PushRequest not found for checkout ID: %s", checkout_request_id
            )
            return jsonify({"success": False, "message": "Transaction not found"}), 404

        payment = push_request.payment
        if not payment:
            current_app.logger.error(
                "Payment not found for PushRequest ID: %s", push_request.id
            )
            return jsonify({"success": False, "message": "Payment record not found"}), 404

        order = payment.order
        if not order:
            current_app.logger.error("Order not found for Payment ID: %s", payment.id)
            return jsonify({"success": False, "message": "Order not found"}), 404

        # Process payment result
        if result_code == 0:
            # Payment successful
            payment.status = "completed"
            payment.mpesa_receipt_number = next(
                (item["Value"] for item in callback_metadata if item.get("Name") == "MpesaReceiptNumber"),
                None,
            )

            # Add status history records
            status_history = OrderStatusHistory(
                order_id=order.id, 
                old_status=order.status, 
                new_status="confirmed"
            )
            db.session.add(status_history)

            payment_history = OrderStatusHistory(
                order_id=order.id,
                old_status=order.payment_status,
                new_status="completed",
            )
            db.session.add(payment_history)

            # Extract transaction date if available
            transaction_date_str = next(
                (item["Value"] for item in callback_metadata if item.get("Name") == "TransactionDate"),
                None,
            )

            if transaction_date_str:
                try:
                    transaction_date = datetime.strptime(
                        str(transaction_date_str), "%Y%m%d%H%M%S"
                    )
                    payment.created_at = transaction_date
                except ValueError:
                    pass

            # Update order status
            order.status = "confirmed"
            order.payment_status = "completed"
            order.mpesa_transaction_id = payment.mpesa_receipt_number
        else:
            # Payment failed
            payment.status = "failed"
            payment.error_message = result_desc

            # Update order status
            order.status = "cancelled"
            order.payment_status = "failed"

        db.session.commit()

        return jsonify({"success": True, "message": "Callback processed successfully"})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error processing callback: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

# ==================================================================
# ERROR HANDLER
# ==================================================================

@app.errorhandler(500)
def handle_server_error(e):
    """Global 500 error handler"""
    return jsonify({
        'success': False,
        'message': 'Internal server error',
        'error': str(e)
    }), 500
# Nourish Net - M-Pesa Food Ordering System

## Overview

Nourish Net is a full-stack food ordering application with M-Pesa payment intergration.
The system allows users to browse menu items, place orders and make payments via M-Pesa STK push.
It includes user authentication, order management, and payment processing features.

## Features
1. User registration and authentication
2. Menu browsing by categories
3. Shopping cart functionality
4. Order placement and tracking
5. M-Pesa payment integration
6. Order history and status updates
7. Responsive web interface

## Technologies Used
1. **Backend:** Python with Flask framework
2. **Database:** SQLite with SQLAlchelmy ORM
4. **Frontend:** HTML, CSS, JavaScript
5. **Payment Integration:** M-Pesa API (Sandbox)
6. **Authentication:** Session-based with password hashing

## Installation
### Prerequisites
- Python 3.10+
- pip package manager

### Steps
1. Clone the repository
2. Create and activate a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Initialize the database
   ```
   python app.py
   ```
5. The application will be available at `http://localhost:5000`

## Configuration
Before running the application, ensure you have configured the following:
1. **M-Pesa Credentials** (in `app.py`):
- `MPESA_CONSUMER_KEY`
- `MPESA_CONSUMER_SECRET`
- `MPESA_PASSKEY`
- `MPESA_BUSINESS_SHORT_CODE`
- `MPESA_CALLBACK_URL`
  
2. Database Configuration:
The default SQLite database is configured in app.py
Modify `SQLALCHEMY_DATABASE_URI` for other database systems

3.Secret Key:
Change the `SECRET_KEY` in app.py for production use

## API Endpoints
#### 1. Authentication:
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/check-session` - Check active session

#### 2. Menu & Categories:
- `GET /api/categories` - Get all categories
- `GET /api/menu/category/<id>` - Get menu items by category
- `GET /api/menu` - Get all menu items
- `GET /api/menu/<id>` - Get specific menu item

#### 3. Orders:
- `POST /api/orders` - Create new order
- `GET /api/orders` - Get user's orders
- `GET /api/orders/<id>` - Get specific order
- `PUT /api/orders/<id>` - Update order
- `DELETE /api/orders/<id>` - Delete order
- `PUT /api/orders/<id>/status` - Update order status

#### 4. Payments:
- `POST /api/make-payment` - Initiate M-Pesa payment
- `POST /api/query-payment-status` - Query payment status
- `POST /api/mpesa-callback` - M-Pesa callback handler

## Usage
1. Register a new account or login with existing credentials
2. Browse the menu and add items to your cart
3. Proceed to checkout and select payment method
4. For M-Pesa payments, enter your phone number to receive STK push
5. View your order history in the Orders section

## Notes
- This application uses the M-Pesa sandbox environment for testing payments
- For production use, replace sandbox credentials with live credentials
- Ensure proper security measures are implemented before deployment

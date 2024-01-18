# from collections import UserDict
# import datetime 
# import json,time,os
# from functools import wraps
# from flask import Flask, jsonify, request, send_from_directory, url_for
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin
# # from sqlalchemy.orm import class_mapper
# # from werkzeug.utils import secure_filename
# import jwt
# from flask_bcrypt import Bcrypt
# from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
# from datetime import datetime, timedelta
from collections import UserDict
from datetime import datetime, timedelta  # Add this line
from datetime import timedelta

import json, time, os
from functools import wraps
from flask import Flask, Request, jsonify, request, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import jwt
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests




app = Flask(__name__)
CORS(app)

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Keep this as is
app.config['JWT_SECRET_KEY'] = 'secret_secret_key'  # Keep this as is
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Define Customer class (serving as both user and customer)
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    book_type = db.Column(db.Integer, nullable=False)

class Loan(db.Model):
    cust_id = db.Column(db.Integer, db.ForeignKey('customer.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    loan_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)

# Create tables in the database
with app.app_context():
    db.create_all()

# Routes for the RESTful API

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    city = data.get('city')
    age = data.get('age')

    # Check if the username is already taken
    existing_user = Customer.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username is already taken'}), 400

    # Hash and salt the password using Bcrypt
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create a new customer and add to the database
    new_customer = Customer(username=username, password=hashed_password, name=name, city=city, age=age)
    db.session.add(new_customer)
    db.session.commit()

    return jsonify({'message': 'Customer registered successfully'}), 201

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()

#     username = data.get('username')
#     password = data.get('password')

#     # Check if the user exists
#     user = Customer.query.filter_by(username=username).first()

#     if user and bcrypt.check_password_hash(user.password, password):
#         # Generate an access token with an expiration time
#         expires = timedelta(hours=1)  # Use timedelta directly
#         access_token = create_access_token(identity=user.id, expires_delta=expires)
#         print(access_token)
#         return jsonify({'access_token': access_token}), 200
#     else:
#         return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    # Check if the user exists
    user = Customer.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        # Generate an access token with an expiration time
        expires = timedelta(hours=1)
        access_token = create_access_token(identity=user.id, expires_delta=expires)
        print(access_token)
        return jsonify({
            'message': 'Login successful',
            'user_id': user.id,
            'username': user.username,
            'access_token': access_token
        }), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401




# Remaining routes for the library app (your existing code)





# @app.route('/add_book', methods=['POST'])
# @jwt_required()
# def add_book():
#     current_user_id = get_jwt_identity()
    
#     # Access the current user's information if needed
#     current_user = Customer.query.get(current_user_id)
#     print(f"User {current_user.username} is adding a book.")

#     data = request.get_json()
#     name = data.get('name')
#     author = data.get('author')
#     year_published = data.get('year_published')
#     book_type = data.get('book_type')

#     new_book = Book(name=name, author=author, year_published=year_published, book_type=book_type)
#     db.session.add(new_book)
#     db.session.commit()

#     return jsonify({'message': 'Book added successfully'})



# Add this decorator to handle both JSON and form data


@app.route('/add_book', methods=['POST'])
@jwt_required()
def add_book():
    current_user_id = get_jwt_identity()
    
    # Access the current user's information if needed
    current_user = Customer.query.get(current_user_id)
    print(f"User {current_user.username} is adding a book.")

    try:
        data = request.get_json()

        name = data.get('name')
        author = data.get('author')
        year_published = data.get('year_published')
        book_type = data.get('book_type')

        new_book = Book(name=name, author=author, year_published=year_published, book_type=book_type)
        db.session.add(new_book)
        db.session.commit()

        return jsonify({'message': 'Book added successfully'})
    except Exception as e:
        print(f"Error adding book: {e}")
        return jsonify({'error': 'Failed to add book'}), 500

# Add other routes...

# Protected routes requiring JWT
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    return jsonify({'message': f'Hello, User {current_user_id}!'}), 200




# Loan a book - goodddddddddddddddddddd
@app.route('/loan_book', methods=['POST'])
@jwt_required()
def loan_book():
    customer_name = get_jwt_identity()

    
    data = request.get_json()
    
    customer_name = data.get('customer_name')
    book_name = data.get('book_name')
    
    
    print("-----------------------------------------")

    # Search for the book by name in the database
    customer = Customer.query.filter_by(name=customer_name).first()
    book = Book.query.filter_by(name=book_name).first()
        
    if customer and book:
        # Check if the book is already on loan
        existing_loan = Loan.query.filter_by(cust_id=customer.id, book_id=book.id, return_date=None).first()
        if existing_loan:
            return jsonify({'error': 'This book is already on loan'})

        # Perform necessary operations (e.g., update database)
        new_loan = Loan(cust_id=customer.id, book_id=book.id)
        db.session.add(new_loan)
        db.session.commit()

        return jsonify({'message': 'Book loaned successfully'})
    else:
        return jsonify({'error': 'Customer or Book not found'})







@app.route('/loans', methods=['GET'])
@jwt_required()
def get_loans():
    
    
    loans = Loan.query.all()
    loan_list = [{'customer_name': Customer.query.get(loan.cust_id).name,
                  'book_name': Book.query.get(loan.book_id).name,
                  'loan_date': loan.loan_date.strftime('%Y-%m-%d %H:%M:%S'),
                  'return_date': loan.return_date.strftime('%Y-%m-%d %H:%M:%S') if loan.return_date else None}
                 for loan in loans]
    return jsonify({'loans': loan_list})


# Return a book
@app.route('/return_book', methods=['POST'])
@jwt_required()
def return_book():
    data = request.get_json()

    customer_name_return = data.get('customer_name_return')
    book_name_return = data.get('book_name_return')

    # Search for customer and book by name in the database
    customer_return = Customer.query.filter_by(name=customer_name_return).first()
    book_return = Book.query.filter_by(name=book_name_return).first()

    if customer_return and book_return:
        # Check if the book is currently on loan to the specified customer
        existing_loan = Loan.query.filter_by(cust_id=customer_return.id, book_id=book_return.id, return_date=None).first()

        if existing_loan:
            # Perform necessary operations (e.g., update database)
            existing_loan.return_date = datetime.utcnow()
            db.session.commit()

            return jsonify({'message': 'Book returned successfully'})
        else:
            return jsonify({'error': 'This book is not currently on loan to the specified customer'})
    else:
        return jsonify({'error': 'Customer or book not found'})
    
    
# Late Loans Function
@app.route('/late_loans', methods=['GET'])
@jwt_required()
def get_late_loans():
    current_date = datetime.utcnow()

    # Get all loans where return_date is None (i.e., not returned yet)
    active_loans = Loan.query.filter_by(return_date=None).all()

    late_loans_list = []

    for loan in active_loans:
        book = Book.query.get(loan.book_id)
        loan_duration = get_loan_duration(book.book_type)

        if loan_duration is not None:
            due_date = loan.loan_date + timedelta(days=loan_duration)
            if current_date > due_date:
                late_loans_list.append({
                    'customer_name': Customer.query.get(loan.cust_id).name,
                    'book_name': book.name,
                    'loan_date': loan.loan_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'due_date': due_date.strftime('%Y-%m-%d %H:%M:%S')
                })

    return jsonify({'late_loans': late_loans_list})

def get_loan_status(book_id):
    # Check if the book is currently on loan
    active_loan = Loan.query.filter_by(book_id=book_id, return_date=None).first()
    
    if active_loan:
        return 'On Loan'
    else:
        return 'Available'


def get_loan_duration(book_type):
    
    # Map book types to loan durations
    loan_durations = {1: 10, 2: 5, 3: 2}
    return loan_durations.get(book_type)

# Get all customers
@app.route('/customers', methods=['GET'])
@jwt_required()
def get_customers():
    customers = Customer.query.all()
    customer_list = [{'id': customer.id, 'name': customer.name, 'city': customer.city,
                      'age': customer.age} for customer in customers]
    return jsonify({'customers': customer_list})

# Get all books
@app.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    books = Book.query.all()
    book_list = [{'id': book.id, 'name': book.name, 'author': book.author,
                  'year_published': book.year_published, 'book_type': book.book_type}
                 for book in books]
    return jsonify({'books': book_list})

# Find a book by name
@app.route('/find_book', methods=['POST'])
@jwt_required()
def find_book():
    data = request.get_json()

    book_name = data.get('book_name')

    # Search for the book by name in the database
    book = Book.query.filter_by(name=book_name).first()

    if book:
        # Check if the book is currently on loan
        loan_status = get_loan_status(book.id)
        return jsonify({'book_name': book.name, 'author': book.author, 'loan_status': loan_status})
    else:
        return jsonify({'error': 'Book not found'})


# Find a customer by name
@app.route('/find_customer', methods=['POST'])
@jwt_required()
def find_customer():
    data = request.get_json()

    customer_name = data.get('customer_name')

    # Search for the customer by name in the database
    customer = Customer.query.filter_by(name=customer_name).first()

    if customer:
        # Get all loans associated with the customer
        loans = Loan.query.filter_by(cust_id=customer.id).all()
        
        # Format loan information
        loan_info = []
        for loan in loans:
            book = Book.query.get(loan.book_id)
            loan_info.append({
                'book_name': book.name,
                'loan_date': loan.loan_date.strftime('%Y-%m-%d %H:%M:%S'),
                'return_date': loan.return_date.strftime('%Y-%m-%d %H:%M:%S') if loan.return_date else 'Not returned'
            })

        return jsonify({
            'customer_name': customer.name,
            'city': customer.city,
            'age': customer.age,
            'loan_info': loan_info
        })
    else:
        return jsonify({'error': 'Customer not found'})


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
from flask import Blueprint, request, jsonify
from app.models.user import User
from app.utils.db import db
from app.utils.auth import create_access_token

auth_bp = Blueprint('auth', __name__)

VALID_ROLES = ['citizen', 'authority']

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate role
    role = data.get('role', 'citizen')
    if role not in VALID_ROLES:
        return jsonify({'error': 'Invalid role. Must be either "citizen" or "authority"'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
        
    if User.query.filter_by(phone_no=data['phone_no']).first():
        return jsonify({'error': 'Phone number already registered'}), 400
    
    # Create new user
    user = User(
        name=data['name'],
        email=data['email'],
        phone_no=data['phone_no'],
        role=role  # Set user role
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = create_access_token(user.id)
        
        return jsonify({
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error creating user'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Find user by email
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate token
    token = create_access_token(user.id)
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/check-role', methods=['GET'])
def get_roles():
    """Get available roles for registration"""
    return jsonify(VALID_ROLES), 200
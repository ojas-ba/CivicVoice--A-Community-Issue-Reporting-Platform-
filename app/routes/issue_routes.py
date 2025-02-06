from flask import Blueprint, request, jsonify
from sqlalchemy import text
from app.models.issue import Issue
from app.utils.db import db
from app.utils.auth import jwt_required
import base64

issue_bp = Blueprint('issue', __name__)

@issue_bp.route('', methods=['POST'])
@jwt_required
def create_issue():
    data = request.get_json()
    
    # Create new issue
    issue = Issue(
        user_id=request.user_id,
        title=data['title'],
        description=data['description'],
        location=data['location'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        category=data['category'],
        photo_url=data.get('photo'),  # base64 image
        status='reported'
    )
    
    try:
        db.session.add(issue)
        db.session.commit()
        return jsonify(issue.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error creating issue'}), 500

@issue_bp.route('', methods=['GET'])
def get_issues():
    # Get user's location from query params
    user_lat = float(request.args.get('latitude', 0))
    user_lng = float(request.args.get('longitude', 0))
    
    # Haversine formula for 2km radius
    radius_query = text("""
        SELECT *, (
            6371 * acos(
                cos(radians(:user_lat)) * cos(radians(latitude)) *
                cos(radians(longitude) - radians(:user_lng)) +
                sin(radians(:user_lat)) * sin(radians(latitude))
            )
        ) AS distance
        FROM issues
        HAVING distance <= 2
        ORDER BY created_at DESC
    """)
    
    try:
        result = db.session.execute(
            radius_query,
            {'user_lat': user_lat, 'user_lng': user_lng}
        )
        
        issues = [dict(row) for row in result]
        return jsonify(issues), 200
    except Exception as e:
        return jsonify({'error': 'Error fetching issues'}), 500

@issue_bp.route('/<int:issue_id>', methods=['GET'])
def get_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    return jsonify(issue.to_dict()), 200

@issue_bp.route('/<int:issue_id>', methods=['DELETE'])
@jwt_required
def delete_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    
    # Check if user owns the issue
    if issue.user_id != request.user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(issue)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error deleting issue'}), 500

# Add to issue_routes.py
@issue_bp.route('/my-issues', methods=['GET'])
@jwt_required
def get_my_issues():
    """Get all issues created by the current user"""
    issues = Issue.query.filter_by(user_id=request.user_id)\
        .order_by(Issue.created_at.desc()).all()
    return jsonify([issue.to_dict() for issue in issues]), 200

@issue_bp.route('/search', methods=['GET'])
def search_issues():
    """Search issues by title, category, or location"""
    query = request.args.get('q', '')
    issues = Issue.query.filter(
        db.or_(
            Issue.title.ilike(f'%{query}%'),
            Issue.location.ilike(f'%{query}%'),
            Issue.category.ilike(f'%{query}%')
        )
    ).all()
    return jsonify([issue.to_dict() for issue in issues]), 200
from flask import Blueprint, request, jsonify
from app.models.status_update import StatusUpdate
from app.models.issue import Issue
from app.models.user import User
from app.utils.db import db
from app.utils.auth import jwt_required
from functools import wraps

status_bp = Blueprint('status', __name__)

def authority_required(f):
    @wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        # Get current user
        user = User.query.get(request.user_id)
        if not user or user.role != 'authority':
            return jsonify({'error': 'Only authorities can perform this action'}), 403
        return f(*args, **kwargs)
    return decorated

@status_bp.route('/<int:issue_id>', methods=['POST'])
@authority_required
def add_status_update(issue_id):
    data = request.get_json()
    
    # Get the issue
    issue = Issue.query.get_or_404(issue_id)
    
    # Create status update
    status_update = StatusUpdate(
        issue_id=issue_id,
        authority_id=request.user_id,
        status=data['status'],
        comment=data.get('comment', '')
    )
    
    # Update issue status
    issue.status = data['status']
    
    try:
        db.session.add(status_update)
        db.session.commit()
        return jsonify(status_update.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error updating status'}), 500

@status_bp.route('/<int:issue_id>', methods=['GET'])
def get_status_history(issue_id):
    # Get all status updates for an issue
    updates = StatusUpdate.query.filter_by(issue_id=issue_id)\
        .order_by(StatusUpdate.created_at.desc())\
        .all()
    
    return jsonify([update.to_dict() for update in updates]), 200

@status_bp.route('/available-statuses', methods=['GET'])
def get_available_statuses():
    # Define available status options
    statuses = [
        'reported',      # Initial state
        'under_review',  # Authority is reviewing
        'in_progress',   # Work started
        'resolved',      # Issue fixed
        'closed'         # Final state
    ]
    
    return jsonify(statuses), 200

@status_bp.route('/dashboard', methods=['GET'])
@authority_required
def authority_dashboard():
    """Get all issues for authority dashboard"""
    try:
        # Get query parameters for filtering
        status = request.args.get('status', None)
        
        # Base query
        query = Issue.query
        
        # Apply status filter if provided
        if status:
            query = query.filter_by(status=status)
        
        # Get issues ordered by creation date
        issues = query.order_by(Issue.created_at.desc()).all()
        
        return jsonify([issue.to_dict() for issue in issues]), 200
        
    except Exception as e:
        return jsonify({'error': 'Error fetching dashboard data'}), 500
    

# Add to status_routes.py
@status_bp.route('/dashboard/stats', methods=['GET'])
@authority_required
def get_dashboard_stats():
    """Get statistics for authority dashboard"""
    stats = {
        'total_issues': Issue.query.count(),
        'pending_issues': Issue.query.filter_by(status='reported').count(),
        'in_progress': Issue.query.filter_by(status='in_progress').count(),
        'resolved': Issue.query.filter_by(status='resolved').count()
    }
    return jsonify(stats), 200
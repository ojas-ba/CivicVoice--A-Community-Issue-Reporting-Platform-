from flask import Blueprint, request, jsonify
from app.models.comment import Comment
from app.models.upvote import Upvote
from app.models.issue import Issue
from app.utils.db import db
from app.utils.auth import jwt_required

social_bp = Blueprint('social', __name__)

# Comment routes
@social_bp.route('/comments/<int:issue_id>', methods=['POST'])
@jwt_required
def add_comment(issue_id):
    data = request.get_json()
    
    comment = Comment(
        issue_id=issue_id,
        user_id=request.user_id,
        content=data['content']
    )
    
    try:
        db.session.add(comment)
        db.session.commit()
        return jsonify(comment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error adding comment'}), 500

@social_bp.route('/comments/<int:issue_id>', methods=['GET'])
def get_comments(issue_id):
    comments = Comment.query.filter_by(issue_id=issue_id)\
        .order_by(Comment.created_at.desc()).all()
    return jsonify([comment.to_dict() for comment in comments]), 200

# Upvote routes
@social_bp.route('/upvotes/<int:issue_id>', methods=['POST'])
@jwt_required
def toggle_upvote(issue_id):
    # Check if upvote exists
    upvote = Upvote.query.filter_by(
        issue_id=issue_id,
        user_id=request.user_id
    ).first()
    
    issue = Issue.query.get_or_404(issue_id)
    
    try:
        if upvote:
            # Remove upvote
            db.session.delete(upvote)
            issue.upvotes_count -= 1
        else:
            # Add upvote
            upvote = Upvote(issue_id=issue_id, user_id=request.user_id)
            db.session.add(upvote)
            issue.upvotes_count += 1
        
        db.session.commit()
        return jsonify({'upvoted': not upvote}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error toggling upvote'}), 500

@social_bp.route('/upvotes/<int:issue_id>/status', methods=['GET'])
@jwt_required
def get_upvote_status(issue_id):
    upvote = Upvote.query.filter_by(
        issue_id=issue_id,
        user_id=request.user_id
    ).first()
    
    return jsonify({'upvoted': bool(upvote)}), 200
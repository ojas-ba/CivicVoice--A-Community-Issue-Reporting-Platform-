# models/issue.py
from app.utils.db import db
from datetime import datetime
from typing import Dict
class Issue(db.Model):
    __tablename__ = 'issues'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), default='normal')
    photo_url = db.Column(db.String(255))
    upvotes_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='reported')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    comments = db.relationship('Comment', backref='issue', lazy=True, cascade='all, delete-orphan')
    upvotes = db.relationship('Upvote', backref='issue', lazy=True, cascade='all, delete-orphan')
    status_updates = db.relationship('StatusUpdate', backref='issue', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self) -> Dict[str, any]:
        return {
            'id': self.id,
            'title': self.title,
            'location': self.location,
            'coordinates': {'lat': self.latitude, 'lng': self.longitude},
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'photo_url': self.photo_url,
            'upvotes_count': self.upvotes_count,
            'status': self.status,
            'reporter': self.reporter.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

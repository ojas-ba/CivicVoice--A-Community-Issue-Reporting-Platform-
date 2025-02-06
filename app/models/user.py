# models/user.py
from app.utils.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from typing import Dict, Any
from datetime import datetime
from typing import Dict
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_no = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), default='citizen')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    issues = db.relationship('Issue', backref='reporter', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    status_updates = db.relationship('StatusUpdate', backref='authority', lazy=True)
    
    def set_password(self, password: str) -> None:
        self.password = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)
    
    def to_dict(self) -> Dict[str, any]:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }

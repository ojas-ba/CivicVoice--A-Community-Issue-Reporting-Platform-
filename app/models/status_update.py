from app.utils.db import db
from datetime import datetime
from typing import Dict
class StatusUpdate(db.Model):
    __tablename__ = 'status_updates'
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    authority_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, any]:
        return {
            'id': self.id,
            'status': self.status,
            'comment': self.comment,
            'authority': self.authority.name,
            'created_at': self.created_at.isoformat()
        }
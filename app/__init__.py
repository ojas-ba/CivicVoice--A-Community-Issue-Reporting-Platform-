from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.config import Config
from app.utils.db import db
import datetime

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.issue_routes import issue_bp
    from app.routes.social_routes import social_bp
    from app.routes.status_routes import status_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(issue_bp, url_prefix='/api/issues')
    app.register_blueprint(social_bp, url_prefix='/api/social')
    app.register_blueprint(status_bp, url_prefix='/api/status')
    
    return app
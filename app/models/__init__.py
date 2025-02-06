# models/__init__.py
from app.utils.db import db
from .user import User
from .issue import Issue
from .comment import Comment
from .upvote import Upvote
from .status_update import StatusUpdate
from datetime import datetime
from typing import Dict

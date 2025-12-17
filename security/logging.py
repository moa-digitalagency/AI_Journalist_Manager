from flask import request, session
from models import db, ActivityLog
from datetime import datetime

def log_activity(action: str, entity_type: str = None, entity_id: int = None, details: str = None):
    try:
        log = ActivityLog(
            user_id=session.get('user_id'),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=request.remote_addr if request else None,
            user_agent=request.user_agent.string[:500] if request and request.user_agent else None,
            log_type='activity'
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")

def log_security(action: str, details: str = None):
    try:
        log = ActivityLog(
            user_id=session.get('user_id'),
            action=action,
            details=details,
            ip_address=request.remote_addr if request else None,
            user_agent=request.user_agent.string[:500] if request and request.user_agent else None,
            log_type='security'
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging security: {e}")

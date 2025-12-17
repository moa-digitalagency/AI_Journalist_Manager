from flask import Blueprint, render_template, request
from security.auth import admin_required
from models import ActivityLog
from datetime import datetime, timedelta

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/')
@admin_required
def index():
    log_type = request.args.get('type', 'all')
    days = request.args.get('days', 7, type=int)
    
    since = datetime.utcnow() - timedelta(days=days)
    query = ActivityLog.query.filter(ActivityLog.created_at >= since)
    
    if log_type != 'all':
        query = query.filter_by(log_type=log_type)
    
    logs = query.order_by(ActivityLog.created_at.desc()).limit(500).all()
    
    return render_template('admin/logs/index.html', logs=logs, log_type=log_type, days=days)

@logs_bp.route('/security')
@admin_required
def security():
    days = request.args.get('days', 30, type=int)
    since = datetime.utcnow() - timedelta(days=days)
    
    logs = ActivityLog.query.filter(
        ActivityLog.log_type == 'security',
        ActivityLog.created_at >= since
    ).order_by(ActivityLog.created_at.desc()).all()
    
    return render_template('admin/logs/security.html', logs=logs, days=days)

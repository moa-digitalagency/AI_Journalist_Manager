from flask import Blueprint, render_template
from security.auth import admin_required
from models import Journalist, Subscriber, Article, DailySummary, User, ActivityLog
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@admin_required
def dashboard():
    journalists_count = Journalist.query.count()
    active_journalists = Journalist.query.filter_by(is_active=True).count()
    subscribers_count = Subscriber.query.count()
    articles_count = Article.query.count()
    
    today = datetime.utcnow().date()
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    new_subscribers_week = Subscriber.query.filter(Subscriber.created_at >= week_ago).count()
    articles_week = Article.query.filter(Article.fetched_at >= week_ago).count()
    summaries_week = DailySummary.query.filter(DailySummary.created_at >= week_ago).count()
    
    recent_activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    
    recent_journalists = Journalist.query.order_by(Journalist.created_at.desc()).limit(5).all()
    recent_subscribers = Subscriber.query.order_by(Subscriber.created_at.desc()).limit(5).all()
    
    stats = {
        'journalists': journalists_count,
        'active_journalists': active_journalists,
        'subscribers': subscribers_count,
        'articles': articles_count,
        'new_subscribers_week': new_subscribers_week,
        'articles_week': articles_week,
        'summaries_week': summaries_week
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_activities=recent_activities,
                         recent_journalists=recent_journalists,
                         recent_subscribers=recent_subscribers)

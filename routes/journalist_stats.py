from flask import Blueprint, render_template
from security.auth import admin_required
from models import db, Journalist, Source, Article, DailySummary, FetchStatistics
from datetime import datetime, timedelta
from sqlalchemy import func
from zoneinfo import ZoneInfo

journalist_stats_bp = Blueprint('journalist_stats', __name__)

@journalist_stats_bp.route('/<int:journalist_id>')
@admin_required
def journalist_summary(journalist_id):
    """Display journalist summary with fetch, summary, and send times."""
    journalist = Journalist.query.get_or_404(journalist_id)
    
    # Get current time in journalist's timezone
    try:
        tz = ZoneInfo(journalist.timezone or 'Europe/Paris')
    except:
        tz = ZoneInfo('Europe/Paris')
    
    now_local = datetime.now(tz)
    now_utc = datetime.utcnow()
    
    # Parse scheduled times
    fetch_hour, fetch_minute = map(int, journalist.fetch_time.split(':'))
    summary_hour, summary_minute = map(int, journalist.summary_time.split(':'))
    send_hour, send_minute = map(int, journalist.send_time.split(':'))
    
    # Calculate next scheduled times (in journalist's timezone)
    def get_next_time(hour, minute, reference_time):
        """Calculate next occurrence of a time."""
        next_time = reference_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_time <= reference_time:
            next_time += timedelta(days=1)
        return next_time
    
    next_fetch = get_next_time(fetch_hour, fetch_minute, now_local)
    next_summary = get_next_time(summary_hour, summary_minute, now_local)
    next_send = get_next_time(send_hour, send_minute, now_local)
    
    # Get last events
    last_summary = DailySummary.query.filter_by(journalist_id=journalist_id).order_by(
        DailySummary.created_at.desc()
    ).first()
    
    last_summary_created = last_summary.created_at if last_summary else None
    last_summary_sent = last_summary.sent_at if last_summary else None
    
    # Get last fetch time (most recent across all sources)
    last_fetch_source = Source.query.filter_by(journalist_id=journalist_id).order_by(
        Source.last_fetched_at.desc()
    ).first()
    last_fetch_time = last_fetch_source.last_fetched_at if last_fetch_source else None
    
    # Get today's statistics
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Articles fetched today by source
    today_stats = db.session.query(
        Source.id,
        Source.url,
        Source.source_type,
        Source.name,
        func.count(Article.id).label('article_count')
    ).outerjoin(Article).filter(
        Source.journalist_id == journalist_id,
        Article.fetched_at >= today_start,
        Article.fetched_at <= today_end
    ).group_by(Source.id, Source.url, Source.source_type, Source.name).all()
    
    # Historical statistics (last 7 days per source)
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    source_stats = []
    for source in journalist.sources:
        articles_today = Article.query.filter_by(
            source_id=source.id
        ).filter(Article.fetched_at >= today_start).count()
        
        articles_week = Article.query.filter_by(
            source_id=source.id
        ).filter(Article.fetched_at >= week_ago).count()
        
        source_stats.append({
            'id': source.id,
            'url': source.url,
            'name': source.name,
            'source_type': source.source_type,
            'is_active': source.is_active,
            'last_fetched_at': source.last_fetched_at,
            'articles_today': articles_today,
            'articles_week': articles_week,
            'fetch_count': source.fetch_count,
            'error_count': source.error_count,
            'last_error': source.last_error
        })
    
    # Total articles fetched
    total_articles_today = sum([s['articles_today'] for s in source_stats])
    total_articles_week = Article.query.filter_by(
        journalist_id=journalist_id
    ).filter(Article.fetched_at >= week_ago).count()
    
    # Summaries count
    summaries_today = DailySummary.query.filter_by(journalist_id=journalist_id).filter(
        DailySummary.created_at >= today_start
    ).count()
    
    summaries_sent_today = DailySummary.query.filter_by(journalist_id=journalist_id).filter(
        DailySummary.sent_at >= today_start,
        DailySummary.sent_at.isnot(None)
    ).count()
    
    data = {
        'journalist': journalist,
        'now_local': now_local,
        'fetch_time': journalist.fetch_time,
        'summary_time': journalist.summary_time,
        'send_time': journalist.send_time,
        'next_fetch': next_fetch,
        'next_summary': next_summary,
        'next_send': next_send,
        'last_fetch_time': last_fetch_time,
        'last_summary_created': last_summary_created,
        'last_summary_sent': last_summary_sent,
        'last_summary': last_summary,
        'source_stats': source_stats,
        'total_articles_today': total_articles_today,
        'total_articles_week': total_articles_week,
        'summaries_today': summaries_today,
        'summaries_sent_today': summaries_sent_today,
        'timezone': journalist.timezone
    }
    
    return render_template('admin/journalist_stats.html', **data)

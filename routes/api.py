from flask import Blueprint, jsonify, request, session, redirect, url_for, flash
from models import db, Journalist, Article, Subscriber, DailySummary
from datetime import datetime, timedelta
from sqlalchemy import func
from functools import wraps

api_bp = Blueprint('api', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/stats')
def stats():
    return jsonify({
        'journalists': Journalist.query.count(),
        'subscribers': Subscriber.query.count(),
        'articles': Article.query.count(),
        'summaries': DailySummary.query.count()
    })

@api_bp.route('/stats/chart')
def chart_data():
    days = request.args.get('days', 7, type=int)
    data = {'dates': [], 'articles': [], 'subscribers': []}
    
    for i in range(days - 1, -1, -1):
        date = datetime.utcnow().date() - timedelta(days=i)
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        
        articles = Article.query.filter(
            Article.fetched_at >= start,
            Article.fetched_at <= end
        ).count()
        
        subscribers = Subscriber.query.filter(
            Subscriber.created_at >= start,
            Subscriber.created_at <= end
        ).count()
        
        data['dates'].append(date.strftime('%d/%m'))
        data['articles'].append(articles)
        data['subscribers'].append(subscribers)
    
    return jsonify(data)

@api_bp.route('/services/fetch', methods=['POST'])
@admin_required
def trigger_fetch():
    """Manually trigger article fetching for all sources."""
    try:
        from services.scheduler_service import SchedulerService
        import threading
        
        thread = threading.Thread(target=SchedulerService.fetch_all_sources, daemon=True)
        thread.start()
        
        return jsonify({'success': True, 'message': 'Collecte des articles lancee'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/services/summary', methods=['POST'])
@admin_required
def trigger_summary():
    """Manually trigger summary generation and sending."""
    try:
        from services.scheduler_service import SchedulerService
        import threading
        
        thread = threading.Thread(target=SchedulerService.generate_summaries, daemon=True)
        thread.start()
        
        return jsonify({'success': True, 'message': 'Generation des resumes lancee'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/services/bot/<int:journalist_id>/start', methods=['POST'])
@admin_required
def start_bot(journalist_id):
    """Start a specific journalist bot."""
    try:
        from services.telegram_service import TelegramService
        
        journalist = Journalist.query.get_or_404(journalist_id)
        TelegramService.start_bot(journalist_id, journalist.telegram_token)
        
        return jsonify({'success': True, 'message': f'Bot {journalist.name} demarre'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/services/bot/<int:journalist_id>/stop', methods=['POST'])
@admin_required
def stop_bot(journalist_id):
    """Stop a specific journalist bot."""
    try:
        from services.telegram_service import TelegramService
        
        journalist = Journalist.query.get_or_404(journalist_id)
        TelegramService.stop_bot(journalist_id)
        
        return jsonify({'success': True, 'message': f'Bot {journalist.name} arrete'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/services/status')
@admin_required
def services_status():
    """Get status of all services."""
    from services.telegram_service import TelegramService
    from services.scheduler_service import scheduler
    
    return jsonify({
        'scheduler_running': scheduler.running,
        'active_bots': list(TelegramService.active_bots.keys()),
        'telegram_running': TelegramService.running
    })

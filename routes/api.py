from flask import Blueprint, jsonify, request, session, redirect, url_for, flash
from models import db, Journalist, Article, Subscriber, DailySummary
from datetime import datetime, timedelta
from sqlalchemy import func
from functools import wraps
from services.telegram_service import TelegramService

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

@api_bp.route('/ai/test-model', methods=['POST'])
@admin_required
def test_ai_model():
    """Test an AI model with a sample prompt."""
    from services.ai_service import AIService
    
    data = request.get_json()
    provider = data.get('provider', 'gemini')
    model = data.get('model', 'auto')
    
    # Check if API is available
    if not AIService.is_available(provider):
        api_key_name = {
            'gemini': 'GEMINI_API_KEY',
            'perplexity': 'PERPLEXITY_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'openrouter': 'OPENROUTER_API_KEY'
        }.get(provider, 'API_KEY')
        
        return jsonify({
            'success': False,
            'error': f'{provider.upper()} API not configured. Please set {api_key_name}'
        }), 400
    
    try:
        service = AIService.get_provider_service(provider)
        
        # Simple test prompt
        test_prompt = "Dis-moi bonjour en une phrase"
        
        if provider == 'gemini':
            response = AIService.generate_summary(
                [{'title': 'Test', 'content': test_prompt, 'source': 'Test'}],
                personality='Test',
                writing_style='Test',
                tone='Test',
                language='fr',
                provider=provider,
                model=model
            )
        elif provider == 'openai':
            response = service.generate_summary(
                [{'title': 'Test', 'content': test_prompt, 'source': 'Test'}],
                personality='Test',
                writing_style='Test',
                tone='Test',
                language='fr',
                model=model or 'gpt-4o-mini'
            )
        elif provider == 'openrouter':
            response = service.generate_summary(
                [{'title': 'Test', 'content': test_prompt, 'source': 'Test'}],
                personality='Test',
                writing_style='Test',
                tone='Test',
                language='fr',
                model=model or 'openrouter/auto'
            )
        else:  # perplexity
            response = service.generate_summary(
                [{'title': 'Test', 'content': test_prompt, 'source': 'Test'}],
                personality='Test',
                writing_style='Test',
                tone='Test',
                language='fr'
            )
        
        if response and 'Erreur' not in response:
            return jsonify({
                'success': True,
                'provider': provider,
                'model': model or 'default',
                'response': response[:300] + '...' if len(response) > 300 else response
            })
        else:
            return jsonify({
                'success': False,
                'error': response or 'Model test failed'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/journalist/fetch-bot-photo', methods=['POST'])
def fetch_bot_photo():
    """Fetch and save bot photo from Telegram."""
    try:
        data = request.get_json()
        telegram_token = data.get('telegram_token')
        
        if not telegram_token:
            return jsonify({
                'success': False,
                'error': 'Telegram token is required'
            }), 400
        
        photo_url = TelegramService.get_bot_photo_url(telegram_token)
        
        if photo_url:
            return jsonify({
                'success': True,
                'photo_url': photo_url
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not fetch bot photo. Make sure the bot has a profile picture.'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

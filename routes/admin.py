from flask import Blueprint, render_template
from security.auth import admin_required
from models import Journalist, Subscriber, Article, DailySummary, User, ActivityLog, TokenUsage
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

@admin_bp.route('/statistics')
@admin_required
def statistics():
    # Global stats
    total_journalists = Journalist.query.count()
    active_bots = Journalist.query.filter_by(is_active=True).count()
    total_subscribers = Subscriber.query.count()
    approved_subscribers = Subscriber.query.filter_by(is_approved=True).count()
    
    # Summary stats
    total_summaries = DailySummary.query.count()
    text_summaries = DailySummary.query.filter(DailySummary.audio_url.is_(None)).count()
    audio_summaries = DailySummary.query.filter(DailySummary.audio_url.isnot(None)).count()
    total_sent = DailySummary.query.filter(DailySummary.sent_at.isnot(None)).count()
    
    # Per-journalist stats with separate rows for each model/usage combination
    journalists = Journalist.query.all()
    journalist_stats = []
    total_cost_by_provider = {}
    
    for j in journalists:
        subs = Subscriber.query.filter_by(journalist_id=j.id).count()
        approved_subs = Subscriber.query.filter_by(journalist_id=j.id, is_approved=True).count()
        summaries = DailySummary.query.filter_by(journalist_id=j.id).count()
        audio = DailySummary.query.filter_by(journalist_id=j.id).filter(DailySummary.audio_url.isnot(None)).count()
        sent = sum([s.sent_count for s in DailySummary.query.filter_by(journalist_id=j.id).all()])
        
        # Token usage by provider and model, separated by text/audio
        token_usages = TokenUsage.query.filter_by(journalist_id=j.id).all()
        model_usage_breakdown = {}  # {provider: {model: {usage_type: data}}}
        
        for token_use in token_usages:
            provider = token_use.provider
            model = token_use.model
            usage_type = token_use.usage_type  # 'summary', 'question', 'audio', etc.
            is_audio = 'audio' in usage_type.lower()
            
            if provider not in model_usage_breakdown:
                model_usage_breakdown[provider] = {}
            if model not in model_usage_breakdown[provider]:
                model_usage_breakdown[provider][model] = {
                    'text': {'tokens': 0, 'cost': 0.0},
                    'audio': {'tokens': 0, 'cost': 0.0}
                }
            
            key = 'audio' if is_audio else 'text'
            model_usage_breakdown[provider][model][key]['tokens'] += token_use.total_tokens
            model_usage_breakdown[provider][model][key]['cost'] += token_use.estimated_cost
            
            if provider not in total_cost_by_provider:
                total_cost_by_provider[provider] = 0.0
            total_cost_by_provider[provider] += token_use.estimated_cost
        
        # Create separate rows for each provider + model + usage type combination
        for provider, models in model_usage_breakdown.items():
            for model, usage_types in models.items():
                # Add row for text usage if exists
                if usage_types['text']['tokens'] > 0:
                    journalist_stats.append({
                        'journalist_id': j.id,
                        'name': j.name,
                        'ai_provider': provider,
                        'model': model,
                        'usage_type': 'text',
                        'subscribers': subs,
                        'approved_subscribers': approved_subs,
                        'summaries': summaries,
                        'audio_summaries': audio,
                        'tokens': usage_types['text']['tokens'],
                        'cost': round(usage_types['text']['cost'], 4)
                    })
                
                # Add row for audio usage if exists
                if usage_types['audio']['tokens'] > 0:
                    journalist_stats.append({
                        'journalist_id': j.id,
                        'name': j.name,
                        'ai_provider': provider,
                        'model': model,
                        'usage_type': 'audio',
                        'subscribers': subs,
                        'approved_subscribers': approved_subs,
                        'summaries': summaries,
                        'audio_summaries': audio,
                        'tokens': usage_types['audio']['tokens'],
                        'cost': round(usage_types['audio']['cost'], 4)
                    })
    
    # Per-subscriber stats (top subscribers)
    top_subscribers = Subscriber.query.order_by(Subscriber.messages_count.desc()).limit(10).all()
    subscriber_stats = []
    for s in top_subscribers:
        journalist = Journalist.query.get(s.journalist_id)
        subscriber_stats.append({
            'username': s.telegram_username or f'User {s.telegram_user_id}',
            'journalist': journalist.name if journalist else 'Unknown',
            'plan': s.plan.name if s.plan else 'Trial',
            'messages': s.messages_count,
            'approved': s.is_approved,
            'joined': s.created_at
        })
    
    return render_template('admin/statistics_tokens.html',
                         global_stats={
                             'total_journalists': total_journalists,
                             'active_bots': active_bots,
                             'total_subscribers': total_subscribers,
                             'approved_subscribers': approved_subscribers,
                             'total_summaries': total_summaries,
                             'text_summaries': text_summaries,
                             'audio_summaries': audio_summaries,
                             'total_sent': total_sent
                         },
                         journalist_stats=journalist_stats,
                         subscriber_stats=subscriber_stats,
                         total_cost_by_provider=total_cost_by_provider)

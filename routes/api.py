from flask import Blueprint, jsonify, request
from models import Journalist, Article, Subscriber, DailySummary
from datetime import datetime, timedelta
from sqlalchemy import func

api_bp = Blueprint('api', __name__)

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

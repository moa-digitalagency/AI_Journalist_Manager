from models import db
from datetime import datetime

class DailySummary(db.Model):
    __tablename__ = 'daily_summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    journalist_id = db.Column(db.Integer, db.ForeignKey('journalists.id'), nullable=False)
    summary_text = db.Column(db.Text, nullable=False)
    audio_url = db.Column(db.String(500))
    articles_count = db.Column(db.Integer, default=0)
    sent_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)

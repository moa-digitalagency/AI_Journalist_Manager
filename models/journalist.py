from models import db
from datetime import datetime

class Journalist(db.Model):
    __tablename__ = 'journalists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    telegram_token = db.Column(db.String(255), nullable=False, unique=True)
    telegram_chat_id = db.Column(db.String(50))
    personality = db.Column(db.Text, default="Journaliste professionnel et concis")
    writing_style = db.Column(db.Text, default="Clair, factuel et engageant")
    spelling_style = db.Column(db.String(50), default="standard")
    tone = db.Column(db.String(50), default="neutral")
    language = db.Column(db.String(10), default="fr")
    eleven_labs_voice_id = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_summary_at = db.Column(db.DateTime)
    summary_time = db.Column(db.String(5), default="08:00")
    
    sources = db.relationship('Source', backref='journalist', lazy=True, cascade='all, delete-orphan')
    articles = db.relationship('Article', backref='journalist', lazy=True, cascade='all, delete-orphan')
    subscribers = db.relationship('Subscriber', backref='journalist', lazy=True, cascade='all, delete-orphan')
    summaries = db.relationship('DailySummary', backref='journalist', lazy=True, cascade='all, delete-orphan')

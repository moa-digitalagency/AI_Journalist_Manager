from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Journalist(db.Model):
    __tablename__ = 'journalists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    telegram_token = db.Column(db.String(255), nullable=False, unique=True)
    telegram_chat_id = db.Column(db.String(50))
    personality = db.Column(db.Text, default="Professional and concise news reporter")
    writing_style = db.Column(db.Text, default="Clear, factual, and engaging")
    tone = db.Column(db.String(50), default="neutral")
    language = db.Column(db.String(10), default="fr")
    eleven_labs_voice_id = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_summary_at = db.Column(db.DateTime)
    
    sources = db.relationship('Source', backref='journalist', lazy=True, cascade='all, delete-orphan')
    articles = db.relationship('Article', backref='journalist', lazy=True, cascade='all, delete-orphan')
    subscribers = db.relationship('Subscriber', backref='journalist', lazy=True, cascade='all, delete-orphan')

class Source(db.Model):
    __tablename__ = 'sources'
    
    id = db.Column(db.Integer, primary_key=True)
    journalist_id = db.Column(db.Integer, db.ForeignKey('journalists.id'), nullable=False)
    source_type = db.Column(db.String(20), nullable=False)  # 'website', 'rss', 'twitter'
    url = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    last_fetched_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    journalist_id = db.Column(db.Integer, db.ForeignKey('journalists.id'), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'))
    title = db.Column(db.String(500))
    content = db.Column(db.Text)
    url = db.Column(db.String(500))
    author = db.Column(db.String(200))
    published_at = db.Column(db.DateTime)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)
    keywords = db.Column(db.Text)
    summary = db.Column(db.Text)
    
    source = db.relationship('Source', backref='articles')

class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    
    id = db.Column(db.Integer, primary_key=True)
    journalist_id = db.Column(db.Integer, db.ForeignKey('journalists.id'), nullable=False)
    telegram_user_id = db.Column(db.String(50), nullable=False)
    telegram_username = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    is_approved = db.Column(db.Boolean, default=False)
    trial_start = db.Column(db.DateTime)
    trial_end = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('journalist_id', 'telegram_user_id', name='unique_subscriber'),
    )

class DailySummary(db.Model):
    __tablename__ = 'daily_summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    journalist_id = db.Column(db.Integer, db.ForeignKey('journalists.id'), nullable=False)
    summary_text = db.Column(db.Text, nullable=False)
    audio_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    
    journalist = db.relationship('Journalist', backref='summaries')

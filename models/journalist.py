from models import db
from datetime import datetime

TIMEZONES = [
    ('UTC', 'UTC (Temps universel)'),
    ('Europe/Paris', 'Paris (France)'),
    ('Europe/London', 'Londres (Royaume-Uni)'),
    ('Europe/Brussels', 'Bruxelles (Belgique)'),
    ('Europe/Berlin', 'Berlin (Allemagne)'),
    ('Europe/Madrid', 'Madrid (Espagne)'),
    ('Europe/Rome', 'Rome (Italie)'),
    ('Europe/Zurich', 'Zurich (Suisse)'),
    ('America/New_York', 'New York (USA Est)'),
    ('America/Los_Angeles', 'Los Angeles (USA Ouest)'),
    ('America/Chicago', 'Chicago (USA Centre)'),
    ('America/Toronto', 'Toronto (Canada)'),
    ('America/Montreal', 'Montréal (Canada)'),
    ('Africa/Casablanca', 'Casablanca (Maroc)'),
    ('Africa/Tunis', 'Tunis (Tunisie)'),
    ('Africa/Algiers', 'Alger (Algérie)'),
    ('Africa/Dakar', 'Dakar (Sénégal)'),
    ('Africa/Abidjan', 'Abidjan (Côte d\'Ivoire)'),
    ('Asia/Tokyo', 'Tokyo (Japon)'),
    ('Asia/Shanghai', 'Shanghai (Chine)'),
    ('Asia/Dubai', 'Dubaï (EAU)'),
    ('Australia/Sydney', 'Sydney (Australie)'),
]

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
    timezone = db.Column(db.String(50), default="Europe/Paris")
    eleven_labs_voice_id = db.Column(db.String(100))
    ai_provider = db.Column(db.String(20), default="gemini")  # gemini or perplexity
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_summary_at = db.Column(db.DateTime)
    summary_time = db.Column(db.String(5), default="08:00")
    
    sources = db.relationship('Source', backref='journalist', lazy=True, cascade='all, delete-orphan')
    articles = db.relationship('Article', backref='journalist', lazy=True, cascade='all, delete-orphan')
    subscribers = db.relationship('Subscriber', backref='journalist', lazy=True, cascade='all, delete-orphan')
    summaries = db.relationship('DailySummary', backref='journalist', lazy=True, cascade='all, delete-orphan')

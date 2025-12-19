from models import db
from datetime import datetime

TIMEZONES = [
    # UTC
    ('UTC', 'UTC (Temps universel)'),
    ('Etc/GMT+1', 'GMT-1 (Est)'),
    ('Etc/GMT+2', 'GMT-2 (Est)'),
    ('Etc/GMT+3', 'GMT-3 (Est)'),
    ('Etc/GMT+4', 'GMT-4 (Est)'),
    ('Etc/GMT+5', 'GMT-5 (Est)'),
    ('Etc/GMT+6', 'GMT-6 (Est)'),
    ('Etc/GMT+7', 'GMT-7 (Est)'),
    ('Etc/GMT+8', 'GMT-8 (Est)'),
    ('Etc/GMT+9', 'GMT-9 (Est)'),
    ('Etc/GMT+10', 'GMT-10 (Est)'),
    ('Etc/GMT+11', 'GMT-11 (Est)'),
    ('Etc/GMT+12', 'GMT-12 (Est)'),
    # Europe
    ('Europe/London', 'Londres (Royaume-Uni)'),
    ('Europe/Dublin', 'Dublin (Irlande)'),
    ('Europe/Paris', 'Paris (France)'),
    ('Europe/Amsterdam', 'Amsterdam (Pays-Bas)'),
    ('Europe/Berlin', 'Berlin (Allemagne)'),
    ('Europe/Brussels', 'Bruxelles (Belgique)'),
    ('Europe/Vienna', 'Vienne (Autriche)'),
    ('Europe/Prague', 'Prague (République Tchèque)'),
    ('Europe/Madrid', 'Madrid (Espagne)'),
    ('Europe/Rome', 'Rome (Italie)'),
    ('Europe/Zurich', 'Zurich (Suisse)'),
    ('Europe/Stockholm', 'Stockholm (Suède)'),
    ('Europe/Oslo', 'Oslo (Norvège)'),
    ('Europe/Copenhagen', 'Copenhague (Danemark)'),
    ('Europe/Warsaw', 'Varsovie (Pologne)'),
    ('Europe/Budapest', 'Budapest (Hongrie)'),
    ('Europe/Bucharest', 'Bucarest (Roumanie)'),
    ('Europe/Istanbul', 'Istanbul (Turquie)'),
    ('Europe/Athens', 'Athènes (Grèce)'),
    ('Europe/Moscow', 'Moscou (Russie)'),
    # Afrique
    ('Africa/Casablanca', 'Casablanca (Maroc)'),
    ('Africa/Tunis', 'Tunis (Tunisie)'),
    ('Africa/Algiers', 'Alger (Algérie)'),
    ('Africa/Cairo', 'Le Caire (Égypte)'),
    ('Africa/Lagos', 'Lagos (Nigeria)'),
    ('Africa/Johannesburg', 'Johannesbourg (Afrique du Sud)'),
    ('Africa/Nairobi', 'Nairobi (Kenya)'),
    ('Africa/Dakar', 'Dakar (Sénégal)'),
    ('Africa/Abidjan', 'Abidjan (Côte d\'Ivoire)'),
    ('Africa/Accra', 'Accra (Ghana)'),
    ('Africa/Kinshasa', 'Kinshasa (RDC)'),
    ('Africa/Lusaka', 'Lusaka (Zambie)'),
    # Asie
    ('Asia/Dubai', 'Dubaï (Émirats)'),
    ('Asia/Bangkok', 'Bangkok (Thaïlande)'),
    ('Asia/Shanghai', 'Shanghai (Chine)'),
    ('Asia/Hong_Kong', 'Hong Kong'),
    ('Asia/Singapore', 'Singapour'),
    ('Asia/Tokyo', 'Tokyo (Japon)'),
    ('Asia/Seoul', 'Séoul (Corée du Sud)'),
    ('Asia/Kolkata', 'Calcutta (Inde)'),
    ('Asia/Jakarta', 'Jakarta (Indonésie)'),
    ('Asia/Manila', 'Manille (Philippines)'),
    ('Asia/Ho_Chi_Minh', 'Hô Chi Minh (Vietnam)'),
    ('Asia/Kuala_Lumpur', 'Kuala Lumpur (Malaisie)'),
    ('Asia/Karachi', 'Karachi (Pakistan)'),
    ('Asia/Lahore', 'Lahore (Pakistan)'),
    ('Asia/Dhaka', 'Dhaka (Bangladesh)'),
    # Amériques
    ('America/New_York', 'New York (USA Est)'),
    ('America/Chicago', 'Chicago (USA Centre)'),
    ('America/Denver', 'Denver (USA Montagne)'),
    ('America/Los_Angeles', 'Los Angeles (USA Ouest)'),
    ('America/Anchorage', 'Anchorage (Alaska)'),
    ('Pacific/Honolulu', 'Honolulu (Hawaï)'),
    ('America/Toronto', 'Toronto (Canada)'),
    ('America/Vancouver', 'Vancouver (Canada)'),
    ('America/Mexico_City', 'Mexico City (Mexique)'),
    ('America/Guatemala', 'Guatemala'),
    ('America/San_Salvador', 'San Salvador'),
    ('America/Caracas', 'Caracas (Venezuela)'),
    ('America/Bogota', 'Bogotá (Colombie)'),
    ('America/Lima', 'Lima (Pérou)'),
    ('America/Sao_Paulo', 'São Paulo (Brésil)'),
    ('America/Buenos_Aires', 'Buenos Aires (Argentine)'),
    ('America/Godthab', 'Godthaab (Groenland)'),
    ('America/Montreal', 'Montréal (Canada)'),
    ('America/Jamaica', 'Kingston (Jamaïque)'),
    ('America/Trinidad', 'Port-d\'Espagne (Trinité)'),
    # Océanie
    ('Australia/Sydney', 'Sydney (Australie)'),
    ('Australia/Melbourne', 'Melbourne (Australie)'),
    ('Australia/Brisbane', 'Brisbane (Australie)'),
    ('Australia/Perth', 'Perth (Australie)'),
    ('Australia/Adelaide', 'Adélaïde (Australie)'),
    ('Pacific/Auckland', 'Auckland (Nouvelle-Zélande)'),
    ('Pacific/Fiji', 'Suva (Fidji)'),
    ('Pacific/Tongatapu', 'Nuku\'alofa (Tonga)'),
    ('Pacific/Kiritimati', 'Kiritimati (Kiribati)'),
]

class Journalist(db.Model):
    __tablename__ = 'journalists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo_url = db.Column(db.String(500))
    telegram_token = db.Column(db.String(255), nullable=False, unique=True)
    telegram_chat_id = db.Column(db.String(50))
    personality = db.Column(db.Text, default="Journaliste professionnel et concis")
    writing_style = db.Column(db.Text, default="Clair, factuel et engageant")
    spelling_style = db.Column(db.String(50), default="standard")
    tone = db.Column(db.String(50), default="neutral")
    language = db.Column(db.String(10), default="fr")
    timezone = db.Column(db.String(50), default="Europe/Paris")
    eleven_labs_voice_id = db.Column(db.String(100))
    ai_provider = db.Column(db.String(20), default="gemini")  # gemini, perplexity, openai, openrouter
    ai_model = db.Column(db.String(100), default="auto")  # Specific model name for the provider
    fetch_time = db.Column(db.String(5), default="02:00")
    summary_time = db.Column(db.String(5), default="08:00")
    send_time = db.Column(db.String(5), default="08:00")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_summary_at = db.Column(db.DateTime)
    
    sources = db.relationship('Source', backref='journalist', lazy=True, cascade='all, delete-orphan')
    articles = db.relationship('Article', backref='journalist', lazy=True, cascade='all, delete-orphan')
    subscribers = db.relationship('Subscriber', backref='journalist', lazy=True, cascade='all, delete-orphan')
    summaries = db.relationship('DailySummary', backref='journalist', lazy=True, cascade='all, delete-orphan')

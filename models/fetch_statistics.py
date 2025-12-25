from models import db
from datetime import datetime

class FetchStatistics(db.Model):
    __tablename__ = 'fetch_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    journalist_id = db.Column(db.Integer, db.ForeignKey('journalists.id'), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    articles_fetched = db.Column(db.Integer, default=0)
    last_fetched_at = db.Column(db.DateTime)
    fetch_success = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    journalist = db.relationship('Journalist', backref='fetch_statistics')
    source = db.relationship('Source', backref='fetch_statistics')

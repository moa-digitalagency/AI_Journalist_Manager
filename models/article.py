from models import db
from datetime import datetime

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

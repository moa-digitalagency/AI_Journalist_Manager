from models import db
from datetime import datetime

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration_days = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, default=0)
    features = db.Column(db.Text)
    max_messages_per_day = db.Column(db.Integer, default=-1)
    can_receive_summaries = db.Column(db.Boolean, default=True)
    can_ask_questions = db.Column(db.Boolean, default=True)
    can_receive_audio = db.Column(db.Boolean, default=False)
    is_trial = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

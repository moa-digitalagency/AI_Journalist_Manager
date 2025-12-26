from models import db
from datetime import datetime

class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    
    id = db.Column(db.Integer, primary_key=True)
    journalist_id = db.Column(db.Integer, db.ForeignKey('journalists.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'))
    channel_type = db.Column(db.String(20), default='telegram')  # telegram, whatsapp
    telegram_user_id = db.Column(db.String(50))
    telegram_username = db.Column(db.String(100))
    whatsapp_phone = db.Column(db.String(20))  # Format: +1234567890
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    is_approved = db.Column(db.Boolean, default=False)
    subscription_start = db.Column(db.DateTime)
    subscription_end = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    messages_count = db.Column(db.Integer, default=0)
    last_message_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    plan = db.relationship('SubscriptionPlan', backref='subscribers')
    
    __table_args__ = (
        db.UniqueConstraint('journalist_id', 'telegram_user_id', name='unique_telegram_subscriber'),
    )

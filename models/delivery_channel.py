from models import db
from datetime import datetime

class DeliveryChannel(db.Model):
    __tablename__ = 'delivery_channels'
    
    id = db.Column(db.Integer, primary_key=True)
    journalist_id = db.Column(db.Integer, db.ForeignKey('journalists.id'), nullable=False)
    channel_type = db.Column(db.String(20), nullable=False)  # telegram, email, whatsapp
    is_active = db.Column(db.Boolean, default=True)
    
    # Credentials (encrypted at rest, decrypted when used)
    telegram_token = db.Column(db.String(255))  # For Telegram bots
    telegram_chat_id = db.Column(db.String(50))  # For Telegram chats
    
    # Email SMTP configuration
    email_address = db.Column(db.String(255))  # Recipient email for text
    smtp_server = db.Column(db.String(255))  # e.g., smtp.gmail.com
    smtp_port = db.Column(db.Integer, default=587)  # Usually 587 or 465
    smtp_username = db.Column(db.String(255))  # SMTP username
    smtp_password = db.Column(db.String(255))  # SMTP password (encrypted)
    
    # WhatsApp configuration
    whatsapp_phone_number = db.Column(db.String(20))  # Format: +1234567890
    whatsapp_api_key = db.Column(db.String(255))  # WhatsApp API key (e.g., Twilio)
    whatsapp_account_id = db.Column(db.String(255))  # Account/SID for the service
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DeliveryChannel {self.channel_type} for journalist {self.journalist_id}>'

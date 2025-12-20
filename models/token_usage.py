from models import db
from datetime import datetime

class TokenUsage(db.Model):
    __tablename__ = 'token_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    journalist_id = db.Column(db.Integer, db.ForeignKey('journalists.id'), nullable=False)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('subscribers.id'))
    provider = db.Column(db.String(50), nullable=False)  # perplexity, openai, gemini, openrouter
    model = db.Column(db.String(100), nullable=False)
    usage_type = db.Column(db.String(50), nullable=False)  # summary, question, audio, extraction
    input_tokens = db.Column(db.Integer, default=0)
    output_tokens = db.Column(db.Integer, default=0)
    total_tokens = db.Column(db.Integer, default=0)
    estimated_cost = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    journalist = db.relationship('Journalist', backref='token_usages')
    subscriber = db.relationship('Subscriber', backref='token_usages')
    
    # Pricing per 1M tokens (approximate rates as of 2025)
    PRICING = {
        'perplexity': {
            'input': 0.005,  # $5 per 1M input tokens
            'output': 0.015  # $15 per 1M output tokens
        },
        'openai': {
            'gpt-4o': {'input': 0.005, 'output': 0.015},
            'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
            'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
            'default': {'input': 0.003, 'output': 0.006}
        },
        'gemini': {
            'gemini-2.5-flash': {'input': 0.0375, 'output': 0.15},
            'gemini-1.5-pro': {'input': 0.00375, 'output': 0.015},
            'default': {'input': 0.0025, 'output': 0.0075}
        },
        'openrouter': {
            'default': {'input': 0.005, 'output': 0.015}
        }
    }
    
    @staticmethod
    def calculate_cost(provider, model, input_tokens, output_tokens):
        """Calculate estimated cost based on tokens and provider pricing."""
        pricing = TokenUsage.PRICING.get(provider, {})
        
        if provider == 'openai':
            model_pricing = pricing.get(model, pricing.get('default', {}))
        elif provider == 'gemini':
            model_pricing = pricing.get(model, pricing.get('default', {}))
        else:
            model_pricing = pricing
        
        input_cost = (input_tokens / 1_000_000) * model_pricing.get('input', 0)
        output_cost = (output_tokens / 1_000_000) * model_pricing.get('output', 0)
        
        return round(input_cost + output_cost, 6)

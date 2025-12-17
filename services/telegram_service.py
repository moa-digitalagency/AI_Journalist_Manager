import os
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logger = logging.getLogger(__name__)

class TelegramService:
    active_bots = {}
    
    @classmethod
    async def start_command(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        from app import app
        from models import db, Journalist, Subscriber
        
        journalist_id = context.bot_data.get('journalist_id')
        if not journalist_id:
            await update.message.reply_text("Bot non configuré.")
            return
        
        user = update.effective_user
        
        with app.app_context():
            journalist = Journalist.query.get(journalist_id)
            if not journalist:
                await update.message.reply_text("Journaliste non trouvé.")
                return
            
            subscriber = Subscriber.query.filter_by(
                journalist_id=journalist_id,
                telegram_user_id=str(user.id)
            ).first()
            
            if not subscriber:
                from models import SubscriptionPlan
                trial_plan = SubscriptionPlan.query.filter_by(is_trial=True, is_active=True).first()
                
                subscriber = Subscriber(
                    journalist_id=journalist_id,
                    telegram_user_id=str(user.id),
                    telegram_username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name if hasattr(user, 'last_name') else None,
                    plan_id=trial_plan.id if trial_plan else None,
                    subscription_start=datetime.utcnow(),
                    subscription_end=datetime.utcnow() + timedelta(days=7)
                )
                db.session.add(subscriber)
                db.session.commit()
                
                welcome_msg = f"""Bienvenue ! Je suis {journalist.name}, votre journaliste IA.

Vous bénéficiez d'une période d'essai de 7 jours:
• Résumés quotidiens des actualités
• Posez-moi vos questions sur l'actualité

Tapez /help pour voir les commandes."""
            else:
                welcome_msg = f"Re-bonjour {user.first_name} ! Comment puis-je vous aider ?"
            
            await update.message.reply_text(welcome_msg)
    
    @classmethod
    async def help_command(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """Commandes disponibles:

/start - Démarrer
/help - Aide
/status - Mon abonnement
/latest - Dernier résumé

Posez-moi n'importe quelle question sur l'actualité !"""
        await update.message.reply_text(help_text)
    
    @classmethod
    async def status_command(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        from app import app
        from models import Subscriber
        
        journalist_id = context.bot_data.get('journalist_id')
        user_id = str(update.effective_user.id)
        
        with app.app_context():
            subscriber = Subscriber.query.filter_by(
                journalist_id=journalist_id,
                telegram_user_id=user_id
            ).first()
            
            if not subscriber:
                await update.message.reply_text("Tapez /start pour commencer.")
                return
            
            if subscriber.is_approved:
                status = "Abonnement actif"
                if subscriber.plan:
                    status += f" - {subscriber.plan.name}"
            elif subscriber.subscription_end and subscriber.subscription_end > datetime.utcnow():
                days = (subscriber.subscription_end - datetime.utcnow()).days
                status = f"Période d'essai ({days} jours restants)"
            else:
                status = "Accès expiré"
            
            await update.message.reply_text(f"Statut: {status}")
    
    @classmethod
    async def latest_command(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        from app import app
        from models import Subscriber, DailySummary
        
        journalist_id = context.bot_data.get('journalist_id')
        user_id = str(update.effective_user.id)
        
        with app.app_context():
            subscriber = Subscriber.query.filter_by(
                journalist_id=journalist_id,
                telegram_user_id=user_id
            ).first()
            
            if not subscriber or not cls.is_active(subscriber):
                await update.message.reply_text("Votre accès a expiré.")
                return
            
            summary = DailySummary.query.filter_by(
                journalist_id=journalist_id
            ).order_by(DailySummary.created_at.desc()).first()
            
            if summary:
                await update.message.reply_text(summary.summary_text, parse_mode='Markdown')
            else:
                await update.message.reply_text("Aucun résumé disponible.")
    
    @classmethod
    async def handle_message(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        from app import app
        from models import db, Journalist, Subscriber, Article
        from services.ai_service import AIService
        
        journalist_id = context.bot_data.get('journalist_id')
        user_id = str(update.effective_user.id)
        message = update.message.text
        
        with app.app_context():
            subscriber = Subscriber.query.filter_by(
                journalist_id=journalist_id,
                telegram_user_id=user_id
            ).first()
            
            if not subscriber:
                await update.message.reply_text("Tapez /start pour commencer.")
                return
            
            if not cls.is_active(subscriber):
                await update.message.reply_text("Votre accès a expiré.")
                return
            
            subscriber.messages_count += 1
            subscriber.last_message_at = datetime.utcnow()
            db.session.commit()
            
            journalist = Journalist.query.get(journalist_id)
            articles = Article.query.filter_by(journalist_id=journalist_id).order_by(Article.fetched_at.desc()).limit(50).all()
            
            articles_data = [
                {'title': a.title, 'content': a.content, 'source': a.source.name if a.source else 'Unknown'}
                for a in articles
            ]
            
            response = AIService.answer_question(
                question=message,
                articles=articles_data,
                personality=journalist.personality,
                writing_style=journalist.writing_style,
                tone=journalist.tone,
                language=journalist.language
            )
            
            await update.message.reply_text(response, parse_mode='Markdown')
    
    @staticmethod
    def is_active(subscriber) -> bool:
        if subscriber.is_approved and subscriber.is_active:
            return True
        if subscriber.subscription_end and subscriber.subscription_end > datetime.utcnow():
            return True
        return False
    
    @classmethod
    async def send_to_subscribers(cls, journalist_id: int, text: str, audio_path: str = None):
        from app import app
        from models import Journalist, Subscriber
        
        with app.app_context():
            journalist = Journalist.query.get(journalist_id)
            if not journalist:
                return 0
            
            bot = Bot(token=journalist.telegram_token)
            subscribers = Subscriber.query.filter_by(journalist_id=journalist_id).all()
            sent_count = 0
            
            for subscriber in subscribers:
                if cls.is_active(subscriber):
                    try:
                        await bot.send_message(
                            chat_id=int(subscriber.telegram_user_id),
                            text=text,
                            parse_mode='Markdown'
                        )
                        
                        if audio_path and os.path.exists(audio_path):
                            with open(audio_path, 'rb') as f:
                                await bot.send_audio(
                                    chat_id=int(subscriber.telegram_user_id),
                                    audio=f,
                                    title="Résumé audio"
                                )
                        
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"Error sending to {subscriber.telegram_user_id}: {e}")
            
            return sent_count

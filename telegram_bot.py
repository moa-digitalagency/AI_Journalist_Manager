import os
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from models import db, Journalist, Subscriber, Article
from ai_service import answer_user_question

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

active_bots = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    journalist_id = context.bot_data.get('journalist_id')
    if not journalist_id:
        await update.message.reply_text("Bot non configuré correctement.")
        return
    
    user = update.effective_user
    telegram_user_id = str(user.id)
    
    from app import app
    with app.app_context():
        journalist = Journalist.query.get(journalist_id)
        if not journalist:
            await update.message.reply_text("Journaliste non trouvé.")
            return
        
        subscriber = Subscriber.query.filter_by(
            journalist_id=journalist_id,
            telegram_user_id=telegram_user_id
        ).first()
        
        if not subscriber:
            subscriber = Subscriber(
                journalist_id=journalist_id,
                telegram_user_id=telegram_user_id,
                telegram_username=user.username,
                first_name=user.first_name,
                trial_start=datetime.utcnow(),
                trial_end=datetime.utcnow() + timedelta(days=7)
            )
            db.session.add(subscriber)
            db.session.commit()
            
            welcome_msg = f"""Bienvenue ! Je suis {journalist.name}, votre journaliste IA personnel.

Vous bénéficiez d'une période d'essai de 7 jours pendant laquelle vous recevrez:
- Un résumé quotidien des actualités
- La possibilité de me poser des questions

Tapez /help pour voir les commandes disponibles."""
        else:
            welcome_msg = f"Re-bonjour {user.first_name} ! Comment puis-je vous aider aujourd'hui ?"
        
        await update.message.reply_text(welcome_msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """Commandes disponibles:

/start - Démarrer la conversation
/help - Afficher cette aide
/status - Voir votre statut d'abonnement
/latest - Obtenir le dernier résumé

Vous pouvez aussi me poser n'importe quelle question sur l'actualité !"""
    await update.message.reply_text(help_text)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    journalist_id = context.bot_data.get('journalist_id')
    user = update.effective_user
    telegram_user_id = str(user.id)
    
    from app import app
    with app.app_context():
        subscriber = Subscriber.query.filter_by(
            journalist_id=journalist_id,
            telegram_user_id=telegram_user_id
        ).first()
        
        if not subscriber:
            await update.message.reply_text("Vous n'êtes pas encore inscrit. Tapez /start pour commencer.")
            return
        
        if subscriber.is_approved:
            status = "Abonnement actif"
        elif subscriber.trial_end and subscriber.trial_end > datetime.utcnow():
            days_left = (subscriber.trial_end - datetime.utcnow()).days
            status = f"Période d'essai en cours ({days_left} jours restants)"
        else:
            status = "Période d'essai expirée - en attente d'activation"
        
        await update.message.reply_text(f"Statut: {status}")

async def latest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    journalist_id = context.bot_data.get('journalist_id')
    telegram_user_id = str(update.effective_user.id)
    
    from app import app
    with app.app_context():
        subscriber = Subscriber.query.filter_by(
            journalist_id=journalist_id,
            telegram_user_id=telegram_user_id
        ).first()
        
        if not subscriber or not is_subscriber_active(subscriber):
            await update.message.reply_text("Votre accès a expiré. Contactez l'administrateur pour le renouveler.")
            return
        
        from models import DailySummary
        latest_summary = DailySummary.query.filter_by(
            journalist_id=journalist_id
        ).order_by(DailySummary.created_at.desc()).first()
        
        if latest_summary:
            await update.message.reply_text(latest_summary.summary_text, parse_mode='Markdown')
        else:
            await update.message.reply_text("Aucun résumé disponible pour le moment.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    journalist_id = context.bot_data.get('journalist_id')
    telegram_user_id = str(update.effective_user.id)
    user_message = update.message.text
    
    from app import app
    with app.app_context():
        subscriber = Subscriber.query.filter_by(
            journalist_id=journalist_id,
            telegram_user_id=telegram_user_id
        ).first()
        
        if not subscriber:
            await update.message.reply_text("Tapez /start pour commencer.")
            return
        
        if not is_subscriber_active(subscriber):
            await update.message.reply_text("Votre période d'essai a expiré. Contactez l'administrateur pour renouveler votre accès.")
            return
        
        journalist = Journalist.query.get(journalist_id)
        if not journalist:
            await update.message.reply_text("Erreur de configuration.")
            return
        
        articles = Article.query.filter_by(journalist_id=journalist_id).order_by(Article.fetched_at.desc()).limit(50).all()
        
        articles_data = [
            {'title': a.title, 'content': a.content, 'source': a.source.name if a.source else 'Unknown', 'url': a.url}
            for a in articles
        ]
        
        response = answer_user_question(
            question=user_message,
            articles=articles_data,
            personality=journalist.personality,
            writing_style=journalist.writing_style,
            tone=journalist.tone,
            language=journalist.language
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')

def is_subscriber_active(subscriber: Subscriber) -> bool:
    if subscriber.is_approved and subscriber.is_active:
        return True
    if subscriber.trial_end and subscriber.trial_end > datetime.utcnow():
        return True
    return False

def create_bot_application(journalist_id: int, token: str) -> Application:
    application = Application.builder().token(token).build()
    application.bot_data['journalist_id'] = journalist_id
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("latest", latest_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    return application

async def send_summary_to_subscribers(journalist_id: int, summary_text: str, audio_path: str = None):
    from app import app
    with app.app_context():
        journalist = Journalist.query.get(journalist_id)
        if not journalist:
            return
        
        bot = Bot(token=journalist.telegram_token)
        subscribers = Subscriber.query.filter_by(journalist_id=journalist_id).all()
        
        for subscriber in subscribers:
            if is_subscriber_active(subscriber):
                try:
                    await bot.send_message(
                        chat_id=int(subscriber.telegram_user_id),
                        text=summary_text,
                        parse_mode='Markdown'
                    )
                    
                    if audio_path and os.path.exists(audio_path):
                        with open(audio_path, 'rb') as audio_file:
                            await bot.send_audio(
                                chat_id=int(subscriber.telegram_user_id),
                                audio=audio_file,
                                title="Résumé audio du jour"
                            )
                except Exception as e:
                    logger.error(f"Error sending to subscriber {subscriber.telegram_user_id}: {e}")

def start_bot(journalist_id: int, token: str):
    if journalist_id in active_bots:
        return
    
    application = create_bot_application(journalist_id, token)
    active_bots[journalist_id] = application
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(application.initialize())
        loop.run_until_complete(application.start())
        loop.run_until_complete(application.updater.start_polling())
    except Exception as e:
        logger.error(f"Error starting bot for journalist {journalist_id}: {e}")

def stop_bot(journalist_id: int):
    if journalist_id not in active_bots:
        return
    
    application = active_bots[journalist_id]
    loop = asyncio.get_event_loop()
    
    try:
        loop.run_until_complete(application.updater.stop())
        loop.run_until_complete(application.stop())
        loop.run_until_complete(application.shutdown())
    except Exception as e:
        logger.error(f"Error stopping bot for journalist {journalist_id}: {e}")
    
    del active_bots[journalist_id]

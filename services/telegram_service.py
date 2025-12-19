import os
import logging
import asyncio
import threading
import requests
from datetime import datetime, timedelta
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

class TelegramService:
    _loop = None
    _thread = None
    active_bots = {}
    running = False
    
    @classmethod
    def get_bot_photo_url(cls, token: str) -> str:
        """Retrieve and save bot profile photo from Telegram."""
        try:
            async def fetch_bot_photo():
                bot = Bot(token=token)
                
                try:
                    bot_info = await bot.get_me()
                    if not bot_info or not bot_info.username:
                        logger.warning(f"Could not get bot info for token")
                        return None
                    
                    user_profile_photos = await bot.get_user_profile_photos(bot_info.id, limit=1)
                    if not user_profile_photos or not user_profile_photos.photos:
                        logger.info(f"Bot {bot_info.username} has no profile photo")
                        return None
                    
                    file_id = user_profile_photos.photos[0][0].file_id
                    file_obj = await bot.get_file(file_id)
                    
                    photo_url = f"https://api.telegram.org/file/bot{token}/{file_obj.file_path}"
                    photo_data = requests.get(photo_url, timeout=30).content
                    
                    filename = secure_filename(f"bot_{bot_info.username}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg")
                    os.makedirs('static/uploads/journalists', exist_ok=True)
                    filepath = os.path.join('static/uploads/journalists', filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(photo_data)
                    
                    logger.info(f"Bot photo saved for {bot_info.username}")
                    return f"/static/uploads/journalists/{filename}"
                finally:
                    await bot.close()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(fetch_bot_photo())
            loop.close()
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving bot photo: {e}")
            return None
    
    @classmethod
    def _get_event_loop(cls):
        """Get or create the shared event loop for all bots."""
        if cls._loop is None or cls._loop.is_closed():
            cls._loop = asyncio.new_event_loop()
        return cls._loop
    
    @classmethod
    async def start_command(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        from app import app
        from models import db, Journalist, Subscriber
        
        journalist_id = context.bot_data.get('journalist_id')
        if not journalist_id:
            await update.message.reply_text("Bot non configure.")
            return
        
        user = update.effective_user
        
        with app.app_context():
            journalist = Journalist.query.get(journalist_id)
            if not journalist:
                await update.message.reply_text("Journaliste non trouve.")
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

Vous beneficiez d'une periode d'essai de 7 jours:
- Resumes quotidiens des actualites
- Posez-moi vos questions sur l'actualite

Tapez /help pour voir les commandes."""
            else:
                welcome_msg = f"Re-bonjour {user.first_name} ! Comment puis-je vous aider ?"
            
            await update.message.reply_text(welcome_msg)
    
    @classmethod
    async def help_command(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """Commandes disponibles:

/start - Demarrer
/help - Aide
/status - Mon abonnement
/latest - Dernier resume

Posez-moi n'importe quelle question sur l'actualite !"""
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
                status = f"Periode d'essai ({days} jours restants)"
            else:
                status = "Acces expire"
            
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
                await update.message.reply_text("Votre acces a expire.")
                return
            
            summary = DailySummary.query.filter_by(
                journalist_id=journalist_id
            ).order_by(DailySummary.created_at.desc()).first()
            
            if summary:
                await update.message.reply_text(summary.summary_text)
            else:
                await update.message.reply_text("Aucun resume disponible.")
    
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
                await update.message.reply_text("Votre acces a expire.")
                return
            
            subscriber.messages_count += 1
            subscriber.last_message_at = datetime.utcnow()
            db.session.commit()
            
            journalist = Journalist.query.get(journalist_id)
            
            # Search articles by keywords
            keywords = message.lower().split()
            articles = Article.query.filter_by(journalist_id=journalist_id).order_by(Article.fetched_at.desc()).limit(100).all()
            
            # Filter articles that match keywords
            relevant_articles = []
            for article in articles:
                article_text = f"{article.title} {article.content}".lower()
                if any(kw in article_text for kw in keywords) or len(relevant_articles) < 10:
                    relevant_articles.append(article)
                if len(relevant_articles) >= 20:
                    break
            
            articles_data = [
                {'title': a.title, 'content': a.content, 'source': a.source.name if a.source else 'Unknown', 'url': a.url}
                for a in relevant_articles
            ]
            
            response = AIService.answer_question(
                question=message,
                articles=articles_data,
                personality=journalist.personality,
                writing_style=journalist.writing_style,
                tone=journalist.tone,
                language=journalist.language,
                provider=journalist.ai_provider,
                model=journalist.ai_model
            )
            
            await update.message.reply_text(response)
    
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
                        tasks = [
                            bot.send_message(
                                chat_id=int(subscriber.telegram_user_id),
                                text=text
                            )
                        ]
                        
                        if audio_path and os.path.exists(audio_path):
                            with open(audio_path, 'rb') as f:
                                tasks.append(
                                    bot.send_audio(
                                        chat_id=int(subscriber.telegram_user_id),
                                        audio=f,
                                        title="Resume audio"
                                    )
                                )
                        
                        await asyncio.gather(*tasks)
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"Error sending to {subscriber.telegram_user_id}: {e}")
            
            return sent_count
    
    @classmethod
    async def _run_bot(cls, journalist_id: int, token: str):
        """Run a single bot using Application.run_polling pattern."""
        try:
            app = Application.builder().token(token).build()
            app.bot_data['journalist_id'] = journalist_id
            
            app.add_handler(CommandHandler("start", cls.start_command))
            app.add_handler(CommandHandler("help", cls.help_command))
            app.add_handler(CommandHandler("status", cls.status_command))
            app.add_handler(CommandHandler("latest", cls.latest_command))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cls.handle_message))
            
            cls.active_bots[journalist_id] = app
            logger.info(f"Started bot for journalist {journalist_id}")
            
            await app.initialize()
            await app.start()
            await app.updater.start_polling(drop_pending_updates=True)
            
            # Wait until stopped
            while journalist_id in cls.active_bots and cls.running:
                await asyncio.sleep(1)
            
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
            
        except Exception as e:
            logger.error(f"Bot error for journalist {journalist_id}: {e}")
        finally:
            if journalist_id in cls.active_bots:
                del cls.active_bots[journalist_id]
    
    @classmethod
    def start_bot(cls, journalist_id: int, token: str):
        """Start a Telegram bot for a journalist."""
        if journalist_id in cls.active_bots:
            logger.info(f"Bot for journalist {journalist_id} already running")
            return
        
        if not cls.running:
            cls.running = True
        
        loop = cls._get_event_loop()
        
        if cls._thread is None or not cls._thread.is_alive():
            def run_loop():
                asyncio.set_event_loop(loop)
                loop.run_forever()
            
            cls._thread = threading.Thread(target=run_loop, daemon=True)
            cls._thread.start()
        
        asyncio.run_coroutine_threadsafe(cls._run_bot(journalist_id, token), loop)
    
    @classmethod
    def stop_bot(cls, journalist_id: int):
        """Stop a running bot."""
        if journalist_id in cls.active_bots:
            del cls.active_bots[journalist_id]
            logger.info(f"Stopped bot for journalist {journalist_id}")
    
    @classmethod
    def start_all_bots(cls):
        """Start all active journalist bots."""
        from app import app
        from models import Journalist
        
        with app.app_context():
            journalists = Journalist.query.filter_by(is_active=True).all()
            
            for journalist in journalists:
                if journalist.telegram_token:
                    cls.start_bot(journalist.id, journalist.telegram_token)
        
        cls.running = True
        logger.info(f"Started {len(cls.active_bots)} Telegram bots")
    
    @classmethod
    def stop_all_bots(cls):
        """Stop all running bots."""
        cls.running = False
        
        for journalist_id in list(cls.active_bots.keys()):
            cls.stop_bot(journalist_id)
        
        if cls._loop and not cls._loop.is_closed():
            cls._loop.call_soon_threadsafe(cls._loop.stop)
        
        cls._loop = None
        cls._thread = None
        
        logger.info("Stopped all Telegram bots")

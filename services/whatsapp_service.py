import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Service for handling WhatsApp messages and conversations"""
    
    @staticmethod
    def is_subscriber_approved(subscriber) -> tuple:
        """Check if subscriber is approved and has valid subscription
        
        Returns:
            tuple: (is_approved: bool, message: str)
        """
        if not subscriber:
            return False, "❌ Abonnement non trouvé. Tapez /start pour commencer."
        
        if not subscriber.is_approved:
            return False, """⚠️ Votre compte n'est pas encore validé.
            
Veuillez contacter l'administrateur pour approuver votre compte.
L'admin doit valider votre abonnement avant de pouvoir utiliser les services."""
        
        if not subscriber.is_active:
            return False, "❌ Votre abonnement est désactivé. Contactez l'administrateur."
        
        if subscriber.subscription_end and subscriber.subscription_end < datetime.utcnow():
            return False, "❌ Votre abonnement a expiré. Veuillez vous abonner à nouveau."
        
        return True, ""
    
    @staticmethod
    def handle_message(journalist, subscriber, message: str):
        """Handle WhatsApp message and generate response
        
        Args:
            journalist: Journalist object
            subscriber: Subscriber object
            message: User's message
            
        Returns:
            str: Response message
        """
        try:
            from app import app
            from models import db, Article
            from services.ai_service import AIService
            
            with app.app_context():
                # Update message count and timestamp
                subscriber.messages_count = (subscriber.messages_count or 0) + 1
                subscriber.last_message_at = datetime.utcnow()
                db.session.commit()
                
                # Search articles by keywords
                keywords = message.lower().split()
                articles = Article.query.filter_by(journalist_id=journalist.id).order_by(Article.fetched_at.desc()).limit(100).all()
                
                # Filter articles matching keywords
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
                
                logger.info(f"✓ WhatsApp response sent to subscriber {subscriber.id}")
                return response
                
        except Exception as e:
            logger.error(f"❌ WhatsApp message handler error: {str(e)[:100]}")
            return "❌ Erreur lors du traitement. Veuillez réessayer."
    
    @staticmethod
    def search_articles_by_date(journalist_id: int, target_date: str):
        """Search articles by date (format: DD/MM/YYYY or YYYY-MM-DD)
        
        Args:
            journalist_id: Journalist ID
            target_date: Date string
            
        Returns:
            str: Formatted article list or error message
        """
        try:
            from app import app
            from models import Article
            from datetime import datetime, timedelta
            
            # Parse date
            try:
                if '/' in target_date:
                    date_obj = datetime.strptime(target_date, '%d/%m/%Y')
                else:
                    date_obj = datetime.strptime(target_date, '%Y-%m-%d')
            except ValueError:
                return f"❌ Format de date invalide. Utilisez DD/MM/YYYY ou YYYY-MM-DD"
            
            with app.app_context():
                # Get articles for that day
                start = date_obj.replace(hour=0, minute=0, second=0)
                end = date_obj.replace(hour=23, minute=59, second=59)
                
                articles = Article.query.filter(
                    Article.journalist_id == journalist_id,
                    Article.fetched_at >= start,
                    Article.fetched_at <= end
                ).order_by(Article.fetched_at.desc()).all()
                
                if not articles:
                    return f"📭 Aucun article trouvé pour le {target_date}"
                
                response = f"📰 Articles du {target_date} ({len(articles)} trouvés):\n\n"
                for i, article in enumerate(articles[:10], 1):
                    response += f"{i}. {article.title}\n"
                    response += f"   Source: {article.source.name if article.source else 'Unknown'}\n"
                    response += f"   Heure: {article.fetched_at.strftime('%H:%M')}\n\n"
                
                if len(articles) > 10:
                    response += f"... et {len(articles) - 10} autres articles"
                
                return response
                
        except Exception as e:
            logger.error(f"❌ Article search error: {str(e)[:100]}")
            return "❌ Erreur lors de la recherche. Veuillez réessayer."
    
    @staticmethod
    def get_latest_summary(journalist_id: int):
        """Get latest summary for WhatsApp
        
        Args:
            journalist_id: Journalist ID
            
        Returns:
            str: Summary text or message
        """
        try:
            from app import app
            from models import DailySummary
            
            with app.app_context():
                summary = DailySummary.query.filter_by(journalist_id=journalist_id).order_by(DailySummary.created_at.desc()).first()
                
                if summary:
                    return summary.summary_text
                else:
                    return "📭 Aucun résumé disponible pour le moment."
                    
        except Exception as e:
            logger.error(f"❌ Summary fetch error: {str(e)[:100]}")
            return "❌ Erreur lors de la récupération. Veuillez réessayer."

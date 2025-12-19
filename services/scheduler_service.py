import logging
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

class SchedulerService:
    
    @staticmethod
    def get_journalist_local_time(journalist):
        """Get current time in journalist's timezone."""
        try:
            tz = ZoneInfo(journalist.timezone or 'Europe/Paris')
            return datetime.now(tz)
        except Exception:
            return datetime.now(ZoneInfo('Europe/Paris'))
    
    @staticmethod
    def should_send_summary(journalist):
        """Check if it's time to send summary based on journalist's timezone."""
        local_time = SchedulerService.get_journalist_local_time(journalist)
        summary_hour = int(journalist.summary_time.split(':')[0]) if journalist.summary_time else 8
        summary_minute = int(journalist.summary_time.split(':')[1]) if journalist.summary_time and ':' in journalist.summary_time else 0
        
        return local_time.hour == summary_hour and local_time.minute < 30
    
    @staticmethod
    def fetch_all_sources():
        from app import app
        from models import db, Journalist, Source, Article
        from services.scraper_service import ScraperService
        from services.ai_service import AIService
        
        with app.app_context():
            journalists = Journalist.query.filter_by(is_active=True).all()
            
            for journalist in journalists:
                logger.info(f"Fetching for: {journalist.name}")
                
                for source in journalist.sources:
                    if not source.is_active:
                        continue
                    
                    try:
                        articles_data = ScraperService.fetch_source(source.source_type, source.url)
                        
                        for data in articles_data:
                            existing = Article.query.filter_by(
                                journalist_id=journalist.id,
                                url=data['url']
                            ).first() if data['url'] else None
                            
                            if not existing:
                                keywords = AIService.extract_keywords(f"{data['title']} {data['content']}")
                                
                                article = Article(
                                    journalist_id=journalist.id,
                                    source_id=source.id,
                                    title=data['title'],
                                    content=data['content'],
                                    url=data['url'],
                                    author=data['author'],
                                    published_at=data['published_at'],
                                    keywords=','.join(keywords)
                                )
                                db.session.add(article)
                        
                        source.last_fetched_at = datetime.utcnow()
                        source.fetch_count += 1
                        db.session.commit()
                        
                    except Exception as e:
                        source.error_count += 1
                        source.last_error = str(e)
                        db.session.commit()
                        logger.error(f"Error fetching {source.url}: {e}")
    
    @staticmethod
    def generate_summaries():
        """Generate summaries respecting each journalist's local timezone."""
        from app import app
        from models import db, Journalist, Article, DailySummary
        from services.ai_service import AIService
        from services.audio_service import AudioService
        from services.telegram_service import TelegramService
        
        with app.app_context():
            journalists = Journalist.query.filter_by(is_active=True).all()
            
            for journalist in journalists:
                try:
                    if not SchedulerService.should_send_summary(journalist):
                        continue
                    
                    local_time = SchedulerService.get_journalist_local_time(journalist)
                    logger.info(f"Generating summary for {journalist.name} (local time: {local_time.strftime('%H:%M')} {journalist.timezone})")
                    
                    yesterday = datetime.utcnow() - timedelta(days=1)
                    articles = Article.query.filter(
                        Article.journalist_id == journalist.id,
                        Article.fetched_at >= yesterday
                    ).all()
                    
                    if not articles:
                        continue
                    
                    articles_data = [
                        {'title': a.title, 'content': a.content, 'source': a.source.name if a.source else 'Unknown'}
                        for a in articles
                    ]
                    
                    ai_summary = AIService.generate_summary(
                        articles=articles_data,
                        personality=journalist.personality,
                        writing_style=journalist.writing_style,
                        tone=journalist.tone,
                        language=journalist.language,
                        provider=journalist.ai_provider,
                        model=journalist.ai_model
                    )
                    
                    # Get unique sources
                    sources = list(set(a.get('source', 'Unknown') for a in articles_data))
                    sources_text = "Sources: " + ", ".join(sources)
                    
                    # Get current time for footer
                    local_time = SchedulerService.get_journalist_local_time(journalist)
                    send_time = local_time.strftime('%d/%m/%Y %H:%M')
                    
                    # Format complete message with summary, sources, journalist name and time
                    summary_text = f"{ai_summary}\n\n{sources_text}\n\n---\n{journalist.name} • {send_time}"
                    
                    audio_path = None
                    if journalist.eleven_labs_voice_id and AudioService.is_available():
                        audio_data = AudioService.generate_audio(ai_summary, journalist.eleven_labs_voice_id)
                        if audio_data:
                            filename = f"summary_{journalist.id}_{datetime.utcnow().strftime('%Y%m%d')}.mp3"
                            audio_path = AudioService.save_audio(audio_data, filename)
                    
                    daily_summary = DailySummary(
                        journalist_id=journalist.id,
                        summary_text=summary_text,
                        audio_url=audio_path,
                        articles_count=len(articles)
                    )
                    db.session.add(daily_summary)
                    journalist.last_summary_at = datetime.utcnow()
                    db.session.commit()
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    sent = loop.run_until_complete(
                        TelegramService.send_to_subscribers(journalist.id, summary_text, audio_path)
                    )
                    loop.close()
                    
                    daily_summary.sent_count = sent
                    daily_summary.sent_at = datetime.utcnow()
                    db.session.commit()
                    
                    logger.info(f"Summary sent for {journalist.name} to {sent} subscribers")
                    
                except Exception as e:
                    logger.error(f"Error for {journalist.name}: {e}")
    
    @classmethod
    def init(cls, fetch_hour=2, summary_hour=8):
        if scheduler.running:
            logger.info("Scheduler already running, skipping init")
            return
        
        scheduler.add_job(
            cls.fetch_all_sources,
            'cron',
            hour=fetch_hour,
            id='fetch_sources',
            replace_existing=True
        )
        
        scheduler.add_job(
            cls.generate_summaries,
            'cron',
            minute=0,
            id='generate_summaries',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info(f"Scheduler: fetch at {fetch_hour}:00, summaries checked every hour (respects journalist timezones)")
    
    @classmethod
    def shutdown(cls):
        scheduler.shutdown()

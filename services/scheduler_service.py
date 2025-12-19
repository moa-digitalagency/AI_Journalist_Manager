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
    def should_fetch(journalist):
        """Check if it's time to fetch articles based on journalist's timezone."""
        local_time = SchedulerService.get_journalist_local_time(journalist)
        fetch_hour = int(journalist.fetch_time.split(':')[0]) if journalist.fetch_time else 2
        fetch_minute = int(journalist.fetch_time.split(':')[1]) if journalist.fetch_time and ':' in journalist.fetch_time else 0
        
        # Execute at the configured hour:minute (within a 1-minute window)
        return local_time.hour == fetch_hour and local_time.minute == fetch_minute
    
    @staticmethod
    def should_generate_summary(journalist):
        """Check if it's time to generate summary based on journalist's timezone."""
        local_time = SchedulerService.get_journalist_local_time(journalist)
        summary_hour = int(journalist.summary_time.split(':')[0]) if journalist.summary_time else 8
        summary_minute = int(journalist.summary_time.split(':')[1]) if journalist.summary_time and ':' in journalist.summary_time else 0
        
        # Execute at the configured hour:minute (within a 1-minute window)
        return local_time.hour == summary_hour and local_time.minute == summary_minute
    
    @staticmethod
    def should_send_summary(journalist):
        """Check if it's time to send summary based on journalist's timezone."""
        local_time = SchedulerService.get_journalist_local_time(journalist)
        send_hour = int(journalist.send_time.split(':')[0]) if journalist.send_time else 8
        send_minute = int(journalist.send_time.split(':')[1]) if journalist.send_time and ':' in journalist.send_time else 0
        
        # Execute at the configured hour:minute (within a 1-minute window)
        return local_time.hour == send_hour and local_time.minute == send_minute
    
    @staticmethod
    def fetch_all_sources():
        from app import app
        from models import db, Journalist, Source, Article
        from services.scraper_service import ScraperService
        from services.ai_service import AIService
        
        with app.app_context():
            journalists = Journalist.query.filter_by(is_active=True).all()
            
            for journalist in journalists:
                # Only fetch if it's the right time for this journalist's timezone
                if not SchedulerService.should_fetch(journalist):
                    continue
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
        
        def generate_audio_async(text, voice_id, journalist_id):
            """Generate audio in parallel."""
            if voice_id and AudioService.is_available():
                audio_data = AudioService.generate_audio(text, voice_id)
                if audio_data:
                    filename = f"summary_{journalist_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp3"
                    return AudioService.save_audio(audio_data, filename)
            return None
        
        with app.app_context():
            journalists = Journalist.query.filter_by(is_active=True).all()
            
            for journalist in journalists:
                try:
                    if not SchedulerService.should_generate_summary(journalist):
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
                    
                    # Get current time for footer
                    local_time = SchedulerService.get_journalist_local_time(journalist)
                    send_date = local_time.strftime('%d/%m/%Y')
                    
                    # Format complete message with greeting, summary, and journalist name
                    greeting = f"Bonjour,\n\nRésumé du {send_date}\n\n"
                    summary_text = f"{greeting}{ai_summary}\n\n---\n{journalist.name}"
                    
                    # Generate audio IN PARALLEL with summary
                    audio_path = generate_audio_async(ai_summary, journalist.eleven_labs_voice_id, journalist.id)
                    
                    daily_summary = DailySummary(
                        journalist_id=journalist.id,
                        summary_text=summary_text,
                        audio_url=audio_path,
                        articles_count=len(articles)
                    )
                    db.session.add(daily_summary)
                    journalist.last_summary_at = datetime.utcnow()
                    db.session.commit()
                    
                    logger.info(f"Summary generated for {journalist.name} with audio: {bool(audio_path)}")
                    
                except Exception as e:
                    logger.error(f"Error generating summary for {journalist.name}: {e}")
    
    @staticmethod
    def send_summaries():
        """Send pending summaries respecting each journalist's send time."""
        from app import app
        from models import db, Journalist, DailySummary
        from services.telegram_service import TelegramService
        
        with app.app_context():
            journalists = Journalist.query.filter_by(is_active=True).all()
            
            for journalist in journalists:
                try:
                    if not SchedulerService.should_send_summary(journalist):
                        continue
                    
                    local_time = SchedulerService.get_journalist_local_time(journalist)
                    logger.info(f"Sending summary for {journalist.name} (local time: {local_time.strftime('%H:%M')} {journalist.timezone})")
                    
                    # Find today's unsent summary
                    today = datetime.utcnow().date()
                    daily_summary = DailySummary.query.filter(
                        DailySummary.journalist_id == journalist.id,
                        DailySummary.created_at >= datetime.combine(today, datetime.min.time()),
                        DailySummary.created_at <= datetime.combine(today, datetime.max.time())
                    ).first()
                    
                    if not daily_summary or daily_summary.sent_at:
                        continue
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    sent = loop.run_until_complete(
                        TelegramService.send_to_subscribers(journalist.id, daily_summary.summary_text, daily_summary.audio_url)
                    )
                    loop.close()
                    
                    daily_summary.sent_count = sent
                    daily_summary.sent_at = datetime.utcnow()
                    db.session.commit()
                    
                    logger.info(f"Summary sent for {journalist.name} to {sent} subscribers")
                    
                except Exception as e:
                    logger.error(f"Error sending summary for {journalist.name}: {e}")
    
    @classmethod
    def init(cls, fetch_hour=2, summary_hour=8):
        if scheduler.running:
            logger.info("Scheduler already running, skipping init")
            return
        
        # Run fetch every minute (checks journalist timezones internally)
        scheduler.add_job(
            cls.fetch_all_sources,
            'cron',
            minute='*',
            id='fetch_sources',
            replace_existing=True
        )
        
        # Run generate every minute (checks journalist timezones internally)
        scheduler.add_job(
            cls.generate_summaries,
            'cron',
            minute='*',
            id='generate_summaries',
            replace_existing=True
        )
        
        # Run send every minute (checks journalist timezones internally)
        scheduler.add_job(
            cls.send_summaries,
            'cron',
            minute='*',
            id='send_summaries',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info(f"Scheduler: running every minute, respects individual journalist fetch/summary/send times and timezones")
    
    @classmethod
    def shutdown(cls):
        scheduler.shutdown()

import logging
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

from models import db, Journalist, Source, Article, DailySummary
from scraper import fetch_source
from ai_service import generate_news_summary, extract_keywords
from audio_service import generate_audio, save_audio_file
from telegram_bot import send_summary_to_subscribers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def fetch_all_sources():
    from app import app
    with app.app_context():
        journalists = Journalist.query.filter_by(is_active=True).all()
        
        for journalist in journalists:
            logger.info(f"Fetching sources for journalist: {journalist.name}")
            
            for source in journalist.sources:
                if not source.is_active:
                    continue
                
                try:
                    articles_data = fetch_source(source.source_type, source.url)
                    
                    for article_data in articles_data:
                        existing = Article.query.filter_by(
                            journalist_id=journalist.id,
                            url=article_data['url']
                        ).first() if article_data['url'] else None
                        
                        if not existing:
                            keywords = extract_keywords(f"{article_data['title']} {article_data['content']}")
                            
                            article = Article(
                                journalist_id=journalist.id,
                                source_id=source.id,
                                title=article_data['title'],
                                content=article_data['content'],
                                url=article_data['url'],
                                author=article_data['author'],
                                published_at=article_data['published_at'],
                                keywords=','.join(keywords)
                            )
                            db.session.add(article)
                    
                    source.last_fetched_at = datetime.utcnow()
                    db.session.commit()
                    
                    logger.info(f"Fetched {len(articles_data)} articles from {source.name or source.url}")
                    
                except Exception as e:
                    logger.error(f"Error fetching source {source.url}: {e}")

def generate_daily_summaries():
    from app import app
    with app.app_context():
        journalists = Journalist.query.filter_by(is_active=True).all()
        
        for journalist in journalists:
            logger.info(f"Generating summary for journalist: {journalist.name}")
            
            try:
                yesterday = datetime.utcnow() - timedelta(days=1)
                articles = Article.query.filter(
                    Article.journalist_id == journalist.id,
                    Article.fetched_at >= yesterday
                ).all()
                
                if not articles:
                    logger.info(f"No new articles for {journalist.name}")
                    continue
                
                articles_data = [
                    {
                        'title': a.title,
                        'content': a.content,
                        'source': a.source.name if a.source else 'Unknown',
                        'url': a.url
                    }
                    for a in articles
                ]
                
                summary_text = generate_news_summary(
                    articles=articles_data,
                    personality=journalist.personality,
                    writing_style=journalist.writing_style,
                    tone=journalist.tone,
                    language=journalist.language
                )
                
                audio_path = None
                if journalist.eleven_labs_voice_id:
                    audio_data = generate_audio(summary_text, journalist.eleven_labs_voice_id)
                    if audio_data:
                        filename = f"summary_{journalist.id}_{datetime.utcnow().strftime('%Y%m%d')}.mp3"
                        audio_path = save_audio_file(audio_data, filename)
                
                daily_summary = DailySummary(
                    journalist_id=journalist.id,
                    summary_text=summary_text,
                    audio_url=audio_path
                )
                db.session.add(daily_summary)
                
                journalist.last_summary_at = datetime.utcnow()
                db.session.commit()
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    send_summary_to_subscribers(journalist.id, summary_text, audio_path)
                )
                loop.close()
                
                daily_summary.sent_at = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"Summary sent for {journalist.name}")
                
            except Exception as e:
                logger.error(f"Error generating summary for {journalist.name}: {e}")

def init_scheduler(app, fetch_hour=2, summary_hour=8):
    scheduler.add_job(
        fetch_all_sources,
        'cron',
        hour=fetch_hour,
        minute=0,
        id='fetch_sources',
        replace_existing=True
    )
    
    scheduler.add_job(
        generate_daily_summaries,
        'cron',
        hour=summary_hour,
        minute=0,
        id='generate_summaries',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info(f"Scheduler started - Fetching at {fetch_hour}:00, Summaries at {summary_hour}:00")

def shutdown_scheduler():
    scheduler.shutdown()

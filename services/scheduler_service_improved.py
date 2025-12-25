"""
Improved Scheduler Service integration example.
Shows how to use ImprovedScraperService with last_fetched_at tracking.
"""

# In scheduler_service.py, replace the fetch_all_sources method with:

def fetch_all_sources_improved(self):
    """Fetch sources with incremental updates (only new content since last fetch)."""
    from app import app
    from models import db, Journalist, Source, Article
    from services.scraper_service_improved import ImprovedScraperService
    from services.ai_service import AIService
    from datetime import datetime
    
    with app.app_context():
        journalists = Journalist.query.filter_by(is_active=True).all()
        
        for journalist in journalists:
            # Only fetch if it's the right time for this journalist's timezone
            if not self.should_fetch(journalist):
                continue
            
            logger.info(f"Fetching sources for: {journalist.name}")
            
            for source in journalist.sources:
                if not source.is_active:
                    continue
                
                try:
                    # Use last_fetched_at for incremental fetching
                    articles_data = ImprovedScraperService.fetch_source(
                        source.source_type, 
                        source.url,
                        last_fetched_at=source.last_fetched_at  # IMPROVED: Only fetch NEW content
                    )
                    
                    logger.info(f"Source: {source.url}, Articles found: {len(articles_data)}")
                    
                    for data in articles_data:
                        # Double-check for duplicates by URL
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
                            logger.info(f"Added new article: {data['title'][:50]}...")
                    
                    # Update last fetch time
                    source.last_fetched_at = datetime.utcnow()
                    source.fetch_count += 1
                    source.error_count = 0  # Reset error count on success
                    db.session.commit()
                    
                except Exception as e:
                    source.error_count += 1
                    source.last_error = str(e)
                    db.session.commit()
                    logger.error(f"Error fetching {source.url}: {e}")

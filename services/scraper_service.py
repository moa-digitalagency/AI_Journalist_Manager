import requests
from bs4 import BeautifulSoup
import feedparser
import logging
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

class ScraperService:
    
    @staticmethod
    def fetch_rss(url: str) -> list:
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:20]:
                article = {
                    'title': entry.get('title', ''),
                    'content': entry.get('summary', entry.get('description', '')),
                    'url': entry.get('link', ''),
                    'author': entry.get('author', ''),
                    'published_at': None,
                    'source': feed.feed.get('title', urlparse(url).netloc)
                }
                
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        article['published_at'] = datetime(*entry.published_parsed[:6])
                    except:
                        pass
                
                articles.append(article)
            
            return articles
        except Exception as e:
            logger.error(f"Error fetching RSS {url}: {e}")
            return []
    
    @staticmethod
    def scrape_website(url: str) -> list:
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            article_tags = soup.find_all('article')
            if not article_tags:
                article_tags = soup.find_all(['div', 'section'], class_=lambda x: x and any(
                    term in str(x).lower() for term in ['article', 'post', 'news', 'entry']
                ))
            
            for article_tag in article_tags[:10]:
                title_tag = article_tag.find(['h1', 'h2', 'h3', 'a'])
                title = title_tag.get_text(strip=True) if title_tag else ''
                
                link = ''
                if title_tag and title_tag.name == 'a':
                    link = title_tag.get('href', '')
                else:
                    link_tag = article_tag.find('a')
                    if link_tag:
                        link = link_tag.get('href', '')
                
                if link and not link.startswith('http'):
                    parsed = urlparse(url)
                    link = f"{parsed.scheme}://{parsed.netloc}{link}"
                
                paragraphs = article_tag.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
                
                if title:
                    articles.append({
                        'title': title,
                        'content': content[:2000],
                        'url': link,
                        'author': '',
                        'published_at': None,
                        'source': urlparse(url).netloc
                    })
            
            return articles
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return []
    
    @staticmethod
    def fetch_source(source_type: str, url: str) -> list:
        if source_type == 'rss':
            return ScraperService.fetch_rss(url)
        elif source_type == 'website':
            return ScraperService.scrape_website(url)
        elif source_type == 'twitter':
            logger.warning("Twitter/X requires API access")
            return []
        else:
            logger.warning(f"Unknown source type: {source_type}")
            return []

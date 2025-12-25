"""
Improved Scraper Service with incremental fetching for websites, Twitter, and YouTube.
Only fetches new content since last fetch, preventing duplicates and unnecessary processing.
"""
import re
import requests
from bs4 import BeautifulSoup
import feedparser
import logging
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

class ImprovedScraperService:
    """
    Enhanced scraper service that:
    - Tracks last_fetched_at to only fetch new content
    - Uses RSS feeds efficiently
    - Implements RSS-like behavior for websites, Twitter, and YouTube
    - Avoids re-fetching old content
    """
    
    @staticmethod
    def fetch_rss(url: str, last_fetched_at=None) -> list:
        """Fetch RSS with optional timestamp filtering."""
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:20]:
                published_at = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_at = datetime(*entry.published_parsed[:6])
                    except:
                        pass
                
                # Skip if entry is older than last fetch
                if last_fetched_at and published_at and published_at <= last_fetched_at:
                    continue
                
                article = {
                    'title': entry.get('title', ''),
                    'content': entry.get('summary', entry.get('description', '')),
                    'url': entry.get('link', ''),
                    'author': entry.get('author', ''),
                    'published_at': published_at,
                    'source': feed.feed.get('title', urlparse(url).netloc)
                }
                
                articles.append(article)
            
            return articles
        except Exception as e:
            logger.error(f"Error fetching RSS {url}: {e}")
            return []
    
    @staticmethod
    def scrape_website(url: str, last_fetched_at=None) -> list:
        """
        Scrape website with timestamp-based filtering.
        Only returns articles newer than last fetch.
        """
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Try to find article containers
            article_tags = soup.find_all('article')
            if not article_tags:
                article_tags = soup.find_all(['div', 'section'], class_=lambda x: x and any(
                    term in str(x).lower() for term in ['article', 'post', 'news', 'entry', 'item']
                ))
            
            for article_tag in article_tags[:20]:  # Increased from 10
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
                
                # Try to extract published date
                published_at = ImprovedScraperService._extract_date_from_element(article_tag)
                
                # Skip if published before last fetch
                if last_fetched_at and published_at and published_at <= last_fetched_at:
                    continue
                
                paragraphs = article_tag.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
                
                if title:
                    articles.append({
                        'title': title,
                        'content': content[:2000],
                        'url': link,
                        'author': '',
                        'published_at': published_at,
                        'source': urlparse(url).netloc
                    })
            
            return articles
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return []
    
    @staticmethod
    def _extract_date_from_element(element) -> datetime:
        """Extract publication date from HTML element."""
        try:
            # Look for time tag
            time_tag = element.find('time')
            if time_tag:
                date_str = time_tag.get('datetime', '')
                if date_str:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # Look for common date patterns in text
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{1,2}-\d{1,2}-\d{4})',
            ]
            
            text = element.get_text()
            for pattern in date_patterns:
                match = re.search(pattern, text)
                if match:
                    try:
                        date_str = match.group(1)
                        return datetime.strptime(date_str, '%Y-%m-%d')
                    except:
                        pass
            
            return None
        except:
            return None
    
    @staticmethod
    def fetch_twitter_feed(username: str, last_fetched_at=None) -> list:
        """
        Fetch tweets from Twitter/X account using Nitter.
        Only returns tweets newer than last_fetched_at.
        """
        try:
            nitter_instances = [
                f"https://nitter.net/{username}",
                f"https://nitter.privacydev.net/{username}",
                f"https://nitter.wolf.town/{username}",
            ]
            
            articles = []
            
            for nitter_url in nitter_instances:
                try:
                    response = requests.get(nitter_url, headers=HEADERS, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        tweets = soup.find_all('div', class_='timeline-item')
                        if not tweets:
                            tweets = soup.find_all('div', class_='tweet')
                        
                        for tweet in tweets[:30]:  # Get more tweets for filtering
                            try:
                                content_div = tweet.find('div', class_=['tweet-content', 'title'])
                                if not content_div:
                                    content_div = tweet.find('p')
                                
                                if content_div:
                                    content = content_div.get_text(strip=True)
                                    
                                    # Get tweet link
                                    link_tag = tweet.find('a', class_=['tweet-link', 'link'])
                                    tweet_url = ""
                                    if link_tag:
                                        href = link_tag.get('href', '')
                                        if href.startswith('/'):
                                            tweet_url = f"https://twitter.com{href}"
                                        else:
                                            tweet_url = href
                                    
                                    # Get timestamp - Nitter format varies
                                    time_tag = tweet.find('span', class_=['tweet-date', 'time'])
                                    published = None
                                    
                                    if time_tag:
                                        try:
                                            time_text = time_tag.get_text(strip=True)
                                            # Basic parsing for relative times (e.g., "2h")
                                            published = ImprovedScraperService._parse_relative_time(time_text)
                                        except:
                                            pass
                                    
                                    # Skip old tweets
                                    if last_fetched_at and published and published <= last_fetched_at:
                                        continue
                                    
                                    if content:
                                        articles.append({
                                            'title': content[:100] + '...' if len(content) > 100 else content,
                                            'content': content,
                                            'url': tweet_url,
                                            'author': f"@{username}",
                                            'published_at': published,
                                            'source': f"Twitter @{username}"
                                        })
                            except Exception as e:
                                logger.debug(f"Error parsing tweet: {e}")
                                continue
                        
                        if articles:
                            logger.info(f"Fetched {len(articles)} tweets from @{username}")
                            return articles
                            
                except Exception as e:
                    logger.warning(f"Nitter instance {nitter_url} failed: {e}")
                    continue
            
            logger.warning(f"Could not fetch Twitter @{username} from any Nitter instance")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching Twitter @{username}: {e}")
            return []
    
    @staticmethod
    def _parse_relative_time(time_str: str) -> datetime:
        """Convert relative time strings to datetime."""
        try:
            time_str = time_str.lower().strip()
            now = datetime.utcnow()
            
            # Parse patterns like "2h", "30m", "1d"
            match = re.search(r'(\d+)\s*([hmd])', time_str)
            if match:
                value = int(match.group(1))
                unit = match.group(2)
                
                if unit == 'h':
                    return now - timedelta(hours=value)
                elif unit == 'm':
                    return now - timedelta(minutes=value)
                elif unit == 'd':
                    return now - timedelta(days=value)
            
            return None
        except:
            return None
    
    @staticmethod
    def fetch_youtube_channel_rss(url: str, last_fetched_at=None) -> list:
        """
        Fetch YouTube channel videos via RSS feed.
        Only returns videos newer than last_fetched_at.
        """
        try:
            articles = []
            
            channel_type, channel_value = ImprovedScraperService.extract_channel_id(url)
            
            rss_url = None
            if channel_type == 'channel':
                rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_value}"
            else:
                # Try to get channel ID from page
                try:
                    response = requests.get(url, headers=HEADERS, timeout=15)
                    if response.status_code == 200:
                        match = re.search(r'"channelId":"([a-zA-Z0-9_-]+)"', response.text)
                        if match:
                            channel_id = match.group(1)
                            rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                except Exception as e:
                    logger.warning(f"Could not extract channel ID from {url}: {e}")
            
            if not rss_url:
                logger.warning(f"Could not determine RSS feed for YouTube channel: {url}")
                return []
            
            # Fetch RSS feed
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:20]:  # Get more for filtering
                video_id = None
                video_url = entry.get('link', '')
                
                if 'yt:videoId' in entry:
                    video_id = entry['yt:videoId']
                else:
                    video_id = ImprovedScraperService.extract_video_id(video_url)
                
                if not video_id:
                    continue
                
                published_at = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_at = datetime(*entry.published_parsed[:6])
                    except:
                        pass
                
                # Skip videos older than last fetch
                if last_fetched_at and published_at and published_at <= last_fetched_at:
                    continue
                
                title = entry.get('title', '')
                author = entry.get('author', feed.feed.get('title', 'YouTube'))
                
                # Get transcript
                transcript = ImprovedScraperService.get_transcript(video_id)
                
                if transcript:
                    content = transcript[:5000]
                else:
                    content = entry.get('summary', entry.get('description', ''))[:2000]
                
                articles.append({
                    'title': title,
                    'content': content,
                    'url': video_url,
                    'author': author,
                    'published_at': published_at,
                    'source': f"YouTube: {author}"
                })
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching YouTube channel {url}: {e}")
            return []
    
    @staticmethod
    def extract_video_id(url: str) -> str:
        """Extract YouTube video ID from various URL formats."""
        patterns = [
            r'(?:v=|/v/)([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'(?:embed|shorts|live)/([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def extract_channel_id(url: str) -> tuple:
        """Extract YouTube channel ID or username from URL. Returns (type, value)."""
        if '/channel/' in url:
            match = re.search(r'/channel/([a-zA-Z0-9_-]+)', url)
            if match:
                return ('channel', match.group(1))
        elif '/@' in url:
            match = re.search(r'/@([a-zA-Z0-9_-]+)', url)
            if match:
                return ('handle', match.group(1))
        elif '/user/' in url:
            match = re.search(r'/user/([a-zA-Z0-9_-]+)', url)
            if match:
                return ('user', match.group(1))
        elif '/c/' in url:
            match = re.search(r'/c/([a-zA-Z0-9_-]+)', url)
            if match:
                return ('custom', match.group(1))
        return (None, None)
    
    @staticmethod
    def get_transcript(video_id: str, languages: list = None) -> str:
        """Get transcript for a YouTube video."""
        if languages is None:
            languages = ['fr', 'en', 'es', 'de']
        
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            for lang in languages:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    entries = transcript.fetch()
                    text = ' '.join([entry['text'] for entry in entries])
                    return text
                except:
                    continue
            
            try:
                transcript = transcript_list.find_manually_created_transcript(languages)
                entries = transcript.fetch()
                return ' '.join([entry['text'] for entry in entries])
            except:
                pass
            
            try:
                for transcript in transcript_list:
                    entries = transcript.fetch()
                    return ' '.join([entry['text'] for entry in entries])
            except:
                pass
            
            return None
            
        except TranscriptsDisabled:
            logger.warning(f"Transcripts disabled for video {video_id}")
            return None
        except NoTranscriptFound:
            logger.warning(f"No transcript found for video {video_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting transcript for {video_id}: {e}")
            return None
    
    @staticmethod
    def is_youtube_video_url(url: str) -> bool:
        """Check if URL is a single YouTube video (not a channel/playlist)."""
        video_patterns = ['/watch', 'youtu.be/', '/shorts/', '/embed/', '/live/', '/v/', 'v=']
        return any(pattern in url for pattern in video_patterns)
    
    @staticmethod
    def fetch_source(source_type: str, url: str, last_fetched_at=None) -> list:
        """
        Fetch from any source type with optional incremental fetching.
        
        Args:
            source_type: 'rss', 'website', 'twitter', 'youtube'
            url: Source URL
            last_fetched_at: Optional datetime to only fetch newer content
        
        Returns:
            List of articles/items
        """
        if source_type == 'rss':
            return ImprovedScraperService.fetch_rss(url, last_fetched_at)
        
        elif source_type == 'website':
            return ImprovedScraperService.scrape_website(url, last_fetched_at)
        
        elif source_type == 'twitter':
            username = url.replace('https://twitter.com/', '').replace('https://x.com/', '').replace('@', '').strip('/')
            return ImprovedScraperService.fetch_twitter_feed(username, last_fetched_at)
        
        elif source_type == 'youtube':
            # YouTube only supports channel RSS feeds (not individual videos in incremental mode)
            if ImprovedScraperService.is_youtube_video_url(url):
                logger.warning("Individual YouTube videos don't support incremental fetching. Use YouTube channel URLs.")
                return []
            else:
                return ImprovedScraperService.fetch_youtube_channel_rss(url, last_fetched_at)
        
        else:
            logger.warning(f"Unknown source type: {source_type}")
            return []

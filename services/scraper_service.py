import re
import requests
from bs4 import BeautifulSoup
import feedparser
import logging
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

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
    def fetch_twitter(username: str) -> list:
        """
        Fetch tweets from a Twitter/X account using web scraping.
        Note: This is a basic implementation. For production, use Twitter API.
        """
        try:
            # Use nitter instance for scraping (Twitter alternative frontend)
            nitter_instances = [
                f"https://nitter.net/{username}",
                f"https://nitter.privacydev.net/{username}",
            ]
            
            articles = []
            
            for nitter_url in nitter_instances:
                try:
                    response = requests.get(nitter_url, headers=HEADERS, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        tweets = soup.find_all('div', class_='timeline-item')
                        if not tweets:
                            tweets = soup.find_all('div', class_='tweet-body')
                        
                        for tweet in tweets[:15]:
                            content_div = tweet.find('div', class_='tweet-content')
                            if content_div:
                                content = content_div.get_text(strip=True)
                                
                                # Get tweet link
                                link_tag = tweet.find('a', class_='tweet-link')
                                tweet_url = ""
                                if link_tag:
                                    tweet_url = f"https://twitter.com{link_tag.get('href', '')}"
                                
                                # Get timestamp
                                time_tag = tweet.find('span', class_='tweet-date')
                                published = None
                                
                                if content:
                                    articles.append({
                                        'title': content[:100] + '...' if len(content) > 100 else content,
                                        'content': content,
                                        'url': tweet_url,
                                        'author': f"@{username}",
                                        'published_at': published,
                                        'source': f"Twitter @{username}"
                                    })
                        
                        if articles:
                            break
                except Exception as e:
                    logger.warning(f"Nitter instance failed: {e}")
                    continue
            
            # Fallback: create placeholder if nitter fails
            if not articles:
                logger.info(f"Could not fetch Twitter @{username} - nitter unavailable")
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching Twitter @{username}: {e}")
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
            
            # Try to get transcript in preferred languages
            for lang in languages:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    entries = transcript.fetch()
                    text = ' '.join([entry['text'] for entry in entries])
                    return text
                except:
                    continue
            
            # Try any available transcript
            try:
                transcript = transcript_list.find_manually_created_transcript(languages)
                entries = transcript.fetch()
                return ' '.join([entry['text'] for entry in entries])
            except:
                pass
            
            # Try auto-generated
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
    def fetch_youtube_channel(url: str) -> list:
        """Fetch recent videos from a YouTube channel and transcribe them."""
        try:
            articles = []
            
            # Get channel RSS feed
            channel_type, channel_value = ScraperService.extract_channel_id(url)
            
            rss_url = None
            if channel_type == 'channel':
                rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_value}"
            else:
                # Try to get channel ID from page
                try:
                    response = requests.get(url, headers=HEADERS, timeout=15)
                    if response.status_code == 200:
                        # Look for channel ID in page
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
            
            for entry in feed.entries[:5]:  # Limit to 5 most recent videos
                video_id = None
                video_url = entry.get('link', '')
                
                # Extract video ID
                if 'yt:videoId' in entry:
                    video_id = entry['yt:videoId']
                else:
                    video_id = ScraperService.extract_video_id(video_url)
                
                if not video_id:
                    continue
                
                title = entry.get('title', '')
                author = entry.get('author', feed.feed.get('title', 'YouTube'))
                
                published_at = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_at = datetime(*entry.published_parsed[:6])
                    except:
                        pass
                
                # Get transcript
                transcript = ScraperService.get_transcript(video_id)
                
                if transcript:
                    content = transcript[:5000]  # Limit content length
                else:
                    # Use description as fallback
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
    def fetch_youtube_video(url: str) -> list:
        """Fetch and transcribe a single YouTube video."""
        try:
            video_id = ScraperService.extract_video_id(url)
            if not video_id:
                logger.warning(f"Could not extract video ID from: {url}")
                return []
            
            # Get video info from oEmbed
            oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
            try:
                response = requests.get(oembed_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    title = data.get('title', 'YouTube Video')
                    author = data.get('author_name', 'YouTube')
                else:
                    title = 'YouTube Video'
                    author = 'YouTube'
            except:
                title = 'YouTube Video'
                author = 'YouTube'
            
            # Get transcript
            transcript = ScraperService.get_transcript(video_id)
            
            if transcript:
                content = transcript[:5000]
            else:
                content = f"[Transcription non disponible pour cette vidéo: {title}]"
            
            return [{
                'title': title,
                'content': content,
                'url': url,
                'author': author,
                'published_at': None,
                'source': f"YouTube: {author}"
            }]
            
        except Exception as e:
            logger.error(f"Error fetching YouTube video {url}: {e}")
            return []
    
    @staticmethod
    def is_youtube_video_url(url: str) -> bool:
        """Check if URL is a single YouTube video (not a channel/playlist)."""
        video_patterns = [
            '/watch',
            'youtu.be/',
            '/shorts/',
            '/embed/',
            '/live/',
            '/v/',
            'v=',
        ]
        return any(pattern in url for pattern in video_patterns)
    
    @staticmethod
    def fetch_source(source_type: str, url: str) -> list:
        if source_type == 'rss':
            return ScraperService.fetch_rss(url)
        elif source_type == 'website':
            return ScraperService.scrape_website(url)
        elif source_type == 'twitter':
            # Extract username from URL or use directly
            username = url.replace('https://twitter.com/', '').replace('https://x.com/', '').replace('@', '').strip('/')
            return ScraperService.fetch_twitter(username)
        elif source_type == 'youtube':
            # Determine if it's a channel or a single video
            if ScraperService.is_youtube_video_url(url):
                return ScraperService.fetch_youtube_video(url)
            else:
                return ScraperService.fetch_youtube_channel(url)
        else:
            logger.warning(f"Unknown source type: {source_type}")
            return []

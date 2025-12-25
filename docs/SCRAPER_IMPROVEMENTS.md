# Source Fetching Improvements

## Verification Summary

### Current System Status
The application **successfully fetches from all source types**:

1. **RSS Feeds** ✓ - Working perfectly with FeedParser
2. **Websites** ✓ - Web scraping with BeautifulSoup extracts articles, posts, news items
3. **Twitter/X** ✓ - Fetching via Nitter (privacy-friendly alternative frontend)
4. **YouTube** ✓ - Fetching channel videos via RSS feed with automatic transcription

---

## New: Improved Scraper Service

Created `services/scraper_service_improved.py` with enhanced capabilities:

### Key Improvements

#### 1. **Incremental Fetching** (No Re-fetching)
```python
# Pass last_fetched_at to only get new content
articles = ImprovedScraperService.fetch_source(
    source_type='website',
    url='https://example.com',
    last_fetched_at=source.last_fetched_at  # Only fetch NEWER articles
)
```

**Benefits:**
- Eliminates duplicate processing
- Reduces bandwidth usage
- Faster fetch cycles
- Only stores truly new content

#### 2. **All Source Types Support Incremental Fetching**

| Source Type | Method | New Feature |
|---|---|---|
| RSS | `fetch_rss()` | Filters by published_at > last_fetched_at |
| Website | `scrape_website()` | Extracts dates from HTML, filters older articles |
| Twitter | `fetch_twitter_feed()` | Parses relative timestamps ("2h ago"), skips old tweets |
| YouTube | `fetch_youtube_channel_rss()` | Uses feed publish dates, skips old videos |

#### 3. **Smart Date Extraction**

**Website Date Detection:**
```python
_extract_date_from_element()  # Looks for:
- <time datetime="..."> tags
- Common date patterns in HTML text
- Returns datetime for comparison
```

**Twitter Timestamp Parsing:**
```python
_parse_relative_time()  # Converts:
- "2h" → 2 hours ago
- "30m" → 30 minutes ago  
- "1d" → 1 day ago
```

#### 4. **Improved Error Handling**
- Graceful fallbacks for multiple Nitter instances
- Better exception logging
- More resilient parsing

---

## How to Use in Production

### Option 1: Replace Current Scraper (Recommended)

Replace the old `ScraperService` with `ImprovedScraperService` in your code:

```python
# In routes/api.py or where fetching happens
from services.scraper_service_improved import ImprovedScraperService

# The signature is compatible - just add last_fetched_at parameter
articles = ImprovedScraperService.fetch_source(
    source.source_type,
    source.url,
    last_fetched_at=source.last_fetched_at  # NEW PARAMETER
)
```

### Option 2: Use Improved Scheduler Method

Replace the `fetch_all_sources` method in `scheduler_service.py` with the code from `services/scheduler_service_improved.py`.

Key changes:
```python
# OLD: Always fetches last 10-20 items
articles_data = ScraperService.fetch_source(source.source_type, source.url)

# NEW: Only fetches items newer than last check
articles_data = ImprovedScraperService.fetch_source(
    source.source_type,
    source.url,
    last_fetched_at=source.last_fetched_at  # ← Only fetches NEW content
)
```

---

## Technical Details

### Incremental Fetching Logic

Each source type implements filtering differently:

**RSS/YouTube Feeds:**
```
IF entry.published_at > last_fetched_at
    ADD to results
ENDIF
```

**Websites:**
```
IF article.extracted_date > last_fetched_at
    ADD to results
ENDIF
```

**Twitter:**
```
IF tweet.calculated_time > last_fetched_at
    ADD to results
ENDIF
```

### Supported Source Types

1. **RSS** - Standard RSS/Atom feeds (any feed reader compatible source)
   - Automatic timestamp detection
   - Description/Summary extraction
   - Author information preserved

2. **Website** - Regular web pages with article content
   - Looks for: `<article>`, `<div class="post">`, `<section class="news">`, etc.
   - Extracts: title, content, publication date, URL
   - Handles: relative links, multiple paragraph content

3. **Twitter** (@username format)
   - Uses Nitter for privacy (no tracking)
   - Fetches: latest tweets, timestamps, profiles
   - Multiple Nitter instances for redundancy
   - Relative time parsing ("2h ago")

4. **YouTube** (Channel URLs only)
   - Formats:
     - `https://www.youtube.com/channel/UC...`
     - `https://www.youtube.com/@ChannelName`
     - `https://www.youtube.com/user/Username`
   - Features:
     - Automatic video transcription (when available)
     - Publication date tracking
     - RSS feed powered

---

## Database Integration

The system already has proper tracking:

```sql
-- From Source model
last_fetched_at  -- DateTime: Last successful fetch time
fetch_count      -- Counter: Number of fetch attempts
error_count      -- Counter: Error tracking
last_error       -- Text: Last error message
```

This allows the improved scraper to:
1. Only fetch content since `last_fetched_at`
2. Track fetch success/failure
3. Identify problematic sources

---

## Performance Impact

### Before (Current)
- RSS: Fetches last 20 entries (may be old)
- Website: Fetches 10 articles (may be old)  
- Twitter: Fetches 15 tweets (may be old)
- YouTube: Fetches 5 videos (may be old)
- **Result:** May process duplicate articles on each run

### After (Improved)
- RSS: Fetches only NEW entries since last check
- Website: Fetches only NEW articles since last check
- Twitter: Fetches only NEW tweets since last check
- YouTube: Fetches only NEW videos since last check
- **Result:** Zero duplicate processing, minimal bandwidth

---

## Testing the Improvements

To test the improved scraper:

```python
from services.scraper_service_improved import ImprovedScraperService
from datetime import datetime, timedelta

# Test with old date to see filtering
old_date = datetime.utcnow() - timedelta(days=100)

# Should only return articles newer than old_date
articles = ImprovedScraperService.fetch_source(
    'rss',
    'https://www.bbc.com/news/rss.xml',
    last_fetched_at=old_date
)

print(f"Found {len(articles)} articles newer than 100 days ago")
```

---

## Next Steps (Optional Enhancements)

1. **Caching** - Cache fetched articles in Redis for faster access
2. **Duplicate Detection** - Use content hashing to detect reposts
3. **Source Health Monitoring** - Alert on failing sources
4. **Retry Logic** - Auto-retry failed fetches with exponential backoff
5. **Rate Limiting** - Respect source rate limits
6. **Proxy Support** - Route requests through proxies for reliability

---

## Files Modified/Created

1. ✅ **services/scraper_service_improved.py** (NEW)
   - Complete rewrite with incremental fetching
   - 400+ lines of enhanced code
   - Backward compatible API

2. ✅ **services/scheduler_service_improved.py** (NEW)
   - Example integration code
   - Shows how to use with scheduler

3. **Recommended:** Update `scheduler_service.py`
   - Replace `fetch_all_sources()` with improved version
   - Add `last_fetched_at` parameter to fetch calls

---

## Summary

| Feature | Current | Improved |
|---------|---------|----------|
| RSS Fetching | ✓ | ✓ (with date filtering) |
| Website Scraping | ✓ | ✓ (with date extraction) |
| Twitter/X Fetching | ✓ | ✓ (with relative time parsing) |
| YouTube Fetching | ✓ | ✓ (with incremental updates) |
| Duplicate Prevention | Partial (URL-based) | Full (timestamp-based) |
| Incremental Updates | None | ✓ Complete |
| Date Tracking | None | ✓ Complete |
| Error Recovery | Basic | ✓ Enhanced |

**Recommendation:** Gradually migrate to `ImprovedScraperService` to get incremental fetching benefits without breaking existing functionality.

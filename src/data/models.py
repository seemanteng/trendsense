import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, Index
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import relationship
except ImportError:
    print("SQLAlchemy not installed. Please run: pip install sqlalchemy")
    exit(1)

Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(String(100), nullable=False)
    published_at = Column(DateTime, default=datetime.utcnow)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    sentiment_score = Column(Float)
    sentiment_label = Column(String(20))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    
    # Relationships
    topic = relationship("Topic", back_populates="articles")
    
    # Indexes
    __table_args__ = (
        Index("idx_published_at", "published_at"),
        Index("idx_source", "source"),
        Index("idx_sentiment", "sentiment_score"),
    )

class SocialPost(Base):
    __tablename__ = "social_posts"
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False)  # reddit, hackernews
    post_id = Column(String(100), unique=True, nullable=False)
    title = Column(String(500))
    content = Column(Text)
    author = Column(String(100))
    url = Column(String(1000))
    score = Column(Integer)  # upvotes, likes, etc.
    comments_count = Column(Integer)
    created_at = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    sentiment_score = Column(Float)
    sentiment_label = Column(String(20))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    
    # Relationships
    topic = relationship("Topic", back_populates="social_posts")
    
    # Indexes
    __table_args__ = (
        Index("idx_platform", "platform"),
        Index("idx_created_at", "created_at"),
        Index("idx_score", "score"),
    )

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    keywords = Column(Text)  # JSON string of keywords
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_trending = Column(Boolean, default=False)
    trend_score = Column(Float)
    
    # Relationships
    articles = relationship("NewsArticle", back_populates="topic")
    social_posts = relationship("SocialPost", back_populates="topic")
    trend_metrics = relationship("TrendMetric", back_populates="topic")

class TrendMetric(Base):
    __tablename__ = "trend_metrics"
    
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    mention_count = Column(Integer)
    sentiment_avg = Column(Float)
    engagement_score = Column(Float)
    virality_score = Column(Float)
    
    # Relationships
    topic = relationship("Topic", back_populates="trend_metrics")
    
    # Indexes
    __table_args__ = (
        Index("idx_timestamp", "timestamp"),
        Index("idx_topic_timestamp", "topic_id", "timestamp"),
    )

# src/scrapers/news_scraper.py - FIXED VERSION
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
import re

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import requests
    import feedparser
except ImportError:
    print("Missing required packages. Please run: pip install requests feedparser")
    exit(1)

try:
    from newsapi import NewsApiClient
except ImportError:
    print("Warning: newsapi-python not installed. NewsAPI features will be disabled.")
    NewsApiClient = None

try:
    from config.settings import NEWS_API_KEY, LOCAL_NEWS_SOURCES, TARGET_REGION
except ImportError:
    NEWS_API_KEY = None
    LOCAL_NEWS_SOURCES = ["channelnewsasia.com", "straitstimes.com", "todayonline.com"]
    TARGET_REGION = "Singapore"

try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove HTML tags if any
    text = re.sub(r'<[^>]+>', '', text)
    return text

def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    if not url:
        return ""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace('www.', '')
    except:
        return ""

class NewsScraper:
    def __init__(self):
        self.newsapi = NewsApiClient(api_key=NEWS_API_KEY) if NEWS_API_KEY and NewsApiClient else None
        self.local_feeds = self._get_local_rss_feeds()
        
    def _get_local_rss_feeds(self) -> List[str]:
        """Get RSS feeds for local Singapore news sources"""
        feeds = {
            'channelnewsasia.com': 'https://www.channelnewsasia.com/rss-feeds',
            'straitstimes.com': 'https://www.straitstimes.com/rss',
            'todayonline.com': 'https://www.todayonline.com/rss'
        }
        return [feeds.get(source, '') for source in LOCAL_NEWS_SOURCES if source in feeds]
    
    def scrape_newsapi(self, hours_back: int = 24) -> List[Dict]:
        """Scrape news from NewsAPI"""
        if not self.newsapi:
            logger.warning("NewsAPI key not configured")
            return []
        
        try:
            articles = []
            from_date = (datetime.now() - timedelta(hours=hours_back)).strftime('%Y-%m-%d')
            
            response = self.newsapi.get_everything(
                q=f'{TARGET_REGION} OR "Singapore"',
                from_param=from_date,
                language='en',
                sort_by='publishedAt',
                page_size=100
            )
            
            for article in response.get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'content': article.get('content', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'published_at': self._parse_date(article.get('publishedAt')),
                    'scraped_at': datetime.now()
                })
            
            logger.info(f"Scraped {len(articles)} articles from NewsAPI")
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping NewsAPI: {e}")
            return []
    
    def scrape_rss_feeds(self) -> List[Dict]:
        """Scrape local RSS feeds"""
        articles = []
        
        for feed_url in self.local_feeds:
            if not feed_url:
                continue
                
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    articles.append({
                        'title': entry.get('title', ''),
                        'content': entry.get('summary', ''),
                        'url': entry.get('link', ''),
                        'source': extract_domain(entry.get('link', '')),
                        'published_at': self._parse_date(entry.get('published')),
                        'scraped_at': datetime.now()
                    })
                
                logger.info(f"Scraped {len(feed.entries)} articles from {feed_url}")
                
            except Exception as e:
                logger.error(f"Error scraping RSS feed {feed_url}: {e}")
        
        return articles
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats"""
        if not date_str:
            return datetime.now()
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
            except:
                return datetime.now()
    
    def scrape_all(self) -> List[Dict]:
        """Scrape from all sources"""
        articles = []
        
        articles.extend(self.scrape_newsapi())
        articles.extend(self.scrape_rss_feeds())
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        logger.info(f"Total unique articles scraped: {len(unique_articles)}")
        return unique_articles
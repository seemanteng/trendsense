import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict
from newsapi import NewsApiClient
from loguru import logger
from config.settings import NEWS_API_KEY, LOCAL_NEWS_SOURCES, TARGET_REGION
from src.utils.helpers import clean_text, extract_domain

class NewsScraper:
    def __init__(self):
        self.newsapi = NewsApiClient(api_key=NEWS_API_KEY) if NEWS_API_KEY else None
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
            # Get Singapore-specific news
            articles = []
            from_date = (datetime.now() - timedelta(hours=hours_back)).strftime('%Y-%m-%d')
            
            # Search for Singapore-related news
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
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                # Try RSS format
                return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
            except:
                return datetime.now()
    
    def scrape_all(self) -> List[Dict]:
        """Scrape from all sources"""
        articles = []
        
        # Scrape NewsAPI
        articles.extend(self.scrape_newsapi())
        
        # Scrape RSS feeds
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
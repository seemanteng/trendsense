import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from sqlalchemy import create_engine, or_
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.exc import IntegrityError
except ImportError:
    print("SQLAlchemy not installed. Please run: pip install sqlalchemy")
    exit(1)

try:
    from config.settings import DATABASE_URL
    from src.data.models import Base, NewsArticle, SocialPost, Topic, TrendMetric
    from src.utils.logger import logger
except ImportError as e:
    print(f"Import error: {e}")
    DATABASE_URL = "sqlite:///trendsense.db"
    logger = None

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL, echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    def save_articles(self, articles: List[Dict]) -> int:
        """Save news articles to database"""
        saved_count = 0
        
        for article_data in articles:
            try:
                # Check if article already exists
                existing = self.session.query(NewsArticle).filter_by(
                    url=article_data['url']
                ).first()
                
                if existing:
                    continue
                
                article = NewsArticle(
                    title=article_data.get('title', ''),
                    content=article_data.get('content', ''),
                    url=article_data.get('url', ''),
                    source=article_data.get('source', ''),
                    published_at=article_data.get('published_at', datetime.now()),
                    scraped_at=article_data.get('scraped_at', datetime.now()),
                    sentiment_score=article_data.get('sentiment_score'),
                    sentiment_label=article_data.get('sentiment_label')
                )
                
                self.session.add(article)
                saved_count += 1
                
            except Exception as e:
                if logger:
                    logger.error(f"Error saving article: {e}")
                continue
        
        try:
            self.session.commit()
            if logger:
                logger.info(f"Saved {saved_count} new articles to database")
        except Exception as e:
            self.session.rollback()
            if logger:
                logger.error(f"Error committing articles: {e}")
            
        return saved_count
    
    def save_social_posts(self, posts: List[Dict]) -> int:
        """Save social media posts to database"""
        saved_count = 0
        
        for post_data in posts:
            try:
                # Check if post already exists
                existing = self.session.query(SocialPost).filter_by(
                    post_id=post_data['post_id'],
                    platform=post_data['platform']
                ).first()
                
                if existing:
                    continue
                
                post = SocialPost(
                    platform=post_data.get('platform', ''),
                    post_id=post_data.get('post_id', ''),
                    title=post_data.get('title', ''),
                    content=post_data.get('content', ''),
                    author=post_data.get('author', ''),
                    url=post_data.get('url', ''),
                    score=post_data.get('score', 0),
                    comments_count=post_data.get('comments_count', 0),
                    created_at=post_data.get('created_at', datetime.now()),
                    scraped_at=post_data.get('scraped_at', datetime.now()),
                    sentiment_score=post_data.get('sentiment_score'),
                    sentiment_label=post_data.get('sentiment_label')
                )
                
                self.session.add(post)
                saved_count += 1
                
            except Exception as e:
                if logger:
                    logger.error(f"Error saving social post: {e}")
                continue
        
        try:
            self.session.commit()
            if logger:
                logger.info(f"Saved {saved_count} new social posts to database")
        except Exception as e:
            self.session.rollback()
            if logger:
                logger.error(f"Error committing social posts: {e}")
            
        return saved_count
    
    def get_recent_articles(self, hours: int = 24) -> List[NewsArticle]:
        """Get recent articles from database"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return self.session.query(NewsArticle).filter(
            NewsArticle.published_at >= cutoff_time
        ).all()
    
    def get_recent_posts(self, hours: int = 24) -> List[SocialPost]:
        """Get recent social posts from database"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return self.session.query(SocialPost).filter(
            SocialPost.created_at >= cutoff_time
        ).all()
    
    def close(self):
        """Close database session"""
        self.session.close()
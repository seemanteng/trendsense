"""Advanced scheduling with cron-like functionality"""

import sys
from pathlib import Path
import schedule
import time
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.scrapers.news_scraper import NewsScraper
from src.scrapers.reddit_scraper import RedditScraper
from src.data.database_manager import DatabaseManager
from src.nlp.topic_clustering import TopicClusterer
from src.forecasting.trend_predictor import TrendPredictor
from src.utils.logger import logger

def scrape_news():
    """Scheduled news scraping"""
    try:
        scraper = NewsScraper()
        db_manager = DatabaseManager()
        
        articles = scraper.scrape_all()
        if articles:
            db_manager.save_articles(articles)
            logger.info(f"Scheduled scraping: {len(articles)} articles")
    except Exception as e:
        logger.error(f"Error in scheduled news scraping: {e}")

def scrape_social():
    """Scheduled social media scraping"""
    try:
        scraper = RedditScraper()
        db_manager = DatabaseManager()
        
        posts = scraper.scrape_singapore_posts()
        if posts:
            db_manager.save_social_posts(posts)
            logger.info(f"Scheduled scraping: {len(posts)} social posts")
    except Exception as e:
        logger.error(f"Error in scheduled social scraping: {e}")

def update_topics():
    """Scheduled topic clustering update"""
    try:
        clusterer = TopicClusterer()
        clusterer.update_topics()
        logger.info("Scheduled topic clustering completed")
    except Exception as e:
        logger.error(f"Error in scheduled topic clustering: {e}")

def generate_forecasts():
    """Scheduled trend forecasting"""
    try:
        predictor = TrendPredictor()
        predictor.generate_all_forecasts()
        logger.info("Scheduled trend forecasting completed")
    except Exception as e:
        logger.error(f"Error in scheduled forecasting: {e}")

def setup_schedule():
    """Setup the scheduling"""
    # News scraping every 15 minutes
    schedule.every(15).minutes.do(scrape_news)
    
    # Social media scraping every 30 minutes
    schedule.every(30).minutes.do(scrape_social)
    
    # Topic clustering every 2 hours
    schedule.every(2).hours.do(update_topics)
    
    # Trend forecasting every 6 hours
    schedule.every(6).hours.do(generate_forecasts)
    
    logger.info("Scheduler setup completed")

def main():
    """Main scheduler loop"""
    setup_schedule()
    
    logger.info("TrendSense scheduler started...")
    logger.info(f"Started at: {datetime.now()}")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
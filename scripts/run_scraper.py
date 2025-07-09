"""Main scraping script"""

import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.scrapers.news_scraper import NewsScraper
    from src.scrapers.hackernews_scraper import HackerNewsScraper
    from src.data.database_manager import DatabaseManager
    from src.nlp.sentiment_analysis import SentimentAnalyzer
    from config.settings import SCRAPE_INTERVAL
    from src.utils.logger import logger
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install required packages first:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# Try to import Reddit scraper (optional)
try:
    from src.scrapers.reddit_scraper import RedditScraper
    REDDIT_AVAILABLE = True
except ImportError:
    print("Warning: Reddit scraper not available (missing praw package)")
    RedditScraper = None
    REDDIT_AVAILABLE = False

# Try to import topic clustering (optional)
try:
    from src.nlp.topic_clustering import TopicClusterer
    CLUSTERING_AVAILABLE = True
except ImportError:
    print("Warning: Topic clustering not available")
    TopicClusterer = None
    CLUSTERING_AVAILABLE = False

def main():
    """Main scraping loop"""
    # Initialize components
    news_scraper = NewsScraper()
    reddit_scraper = RedditScraper()
    db_manager = DatabaseManager()
    sentiment_analyzer = SentimentAnalyzer()
    topic_clusterer = TopicClusterer()
    
    logger.info("Starting TrendSense scraper...")
    
    while True:
        try:
            # Scrape news articles
            logger.info("Scraping news articles...")
            articles = news_scraper.scrape_all()
            
            # Process and analyze articles
            if articles:
                # Analyze sentiment
                for article in articles:
                    sentiment = sentiment_analyzer.analyze_text(article['content'])
                    article['sentiment_score'] = sentiment['score']
                    article['sentiment_label'] = sentiment['label']
                
                # Save to database
                db_manager.save_articles(articles)
                
                # Cluster topics (run periodically)
                topic_clusterer.update_topics()
                
                logger.info(f"Processed {len(articles)} articles")
            
            # Scrape Reddit posts
            logger.info("Scraping Reddit posts...")
            posts = reddit_scraper.scrape_singapore_posts()
            
            if posts:
                # Analyze sentiment for posts
                for post in posts:
                    sentiment = sentiment_analyzer.analyze_text(post['content'])
                    post['sentiment_score'] = sentiment['score']
                    post['sentiment_label'] = sentiment['label']
                
                # Save to database
                db_manager.save_social_posts(posts)
                
                logger.info(f"Processed {len(posts)} Reddit posts")
            
            # Wait before next scraping cycle
            logger.info(f"Waiting {SCRAPE_INTERVAL} seconds before next scrape...")
            time.sleep(SCRAPE_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Scraping stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    main()
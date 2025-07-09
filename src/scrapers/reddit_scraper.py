# src/scrapers/reddit_scraper.py
"""Reddit scraper using PRAW (Python Reddit API Wrapper)"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Manual environment loading
try:
    from dotenv import load_dotenv
    env_path = PROJECT_ROOT / '.env'
    load_dotenv(env_path)
    print(f"Reddit scraper: Loading .env from {env_path}")
except ImportError:
    print("Warning: python-dotenv not available")

try:
    import praw
except ImportError:
    print("PRAW not installed. Please run: pip install praw")
    praw = None

# Get credentials directly from environment
import os
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "TrendSense/1.0")

print(f"Reddit scraper - CLIENT_ID loaded: {bool(REDDIT_CLIENT_ID)}")
print(f"Reddit scraper - CLIENT_SECRET loaded: {bool(REDDIT_CLIENT_SECRET)}")

try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class RedditScraper:
    def __init__(self):
        if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET]) or not praw:
            logger.warning("Reddit API credentials not configured or PRAW not installed")
            self.reddit = None
            return
            
        try:
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT
            )
            logger.info("Reddit API initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Reddit API: {e}")
            self.reddit = None
    
    def scrape_subreddit(self, subreddit_name: str, limit: int = 100, sort_by: str = 'hot') -> List[Dict]:
        """Scrape posts from a specific subreddit"""
        if not self.reddit:
            return []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get submissions based on sort method
            if sort_by == 'hot':
                submissions = subreddit.hot(limit=limit)
            elif sort_by == 'new':
                submissions = subreddit.new(limit=limit)
            elif sort_by == 'top':
                submissions = subreddit.top(limit=limit, time_filter='week')
            else:
                submissions = subreddit.hot(limit=limit)
            
            posts = []
            for submission in submissions:
                # Skip if post is too old (more than 7 days)
                post_time = datetime.fromtimestamp(submission.created_utc)
                if post_time < datetime.now() - timedelta(days=7):
                    continue
                
                # Get post content
                content = submission.selftext if submission.selftext else submission.title
                
                post = {
                    'post_id': submission.id,
                    'title': submission.title,
                    'content': content,
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'url': f"https://reddit.com{submission.permalink}",
                    'score': submission.score,
                    'comments_count': submission.num_comments,
                    'created_at': post_time,
                    'scraped_at': datetime.now(),
                    'platform': 'reddit',
                    'subreddit': subreddit_name
                }
                posts.append(post)
            
            logger.info(f"Scraped {len(posts)} posts from r/{subreddit_name}")
            return posts
            
        except Exception as e:
            logger.error(f"Error scraping r/{subreddit_name}: {e}")
            return []
    
    def scrape_singapore_subreddits(self) -> List[Dict]:
        """Scrape Singapore-related subreddits including news sources"""
        singapore_subreddits = [
            # Main Singapore subreddits
            'singapore',
            'singaporefi',
            'asksingapore',
            'sgsecret',
            'sgexams',
            'sgfood',
            'sgpolitics',
            'sginvestors',
            'smallbizsingapore',
            
            # Singapore news subreddits
            'straitstimes',     
            'todaynews',
            'channelnewsasia',  
            'nus',          
        ]
        
        all_posts = []
        
        for subreddit in singapore_subreddits:
            # Try both hot and new posts for news subreddits
            if any(news in subreddit.lower() for news in ['times', 'mothership', 'today', 'news', 'cna']):
                # For news subreddits, get more content
                hot_posts = self.scrape_subreddit(subreddit, limit=50, sort_by='hot')
                new_posts = self.scrape_subreddit(subreddit, limit=30, sort_by='new')
                top_posts = self.scrape_subreddit(subreddit, limit=20, sort_by='top')
            else:
                # For regular subreddits, get standard amount
                hot_posts = self.scrape_subreddit(subreddit, limit=25, sort_by='hot')
                new_posts = self.scrape_subreddit(subreddit, limit=25, sort_by='new')
                top_posts = []
            
            all_posts.extend(hot_posts)
            all_posts.extend(new_posts)
            all_posts.extend(top_posts)
        
        # Remove duplicates based on post_id
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post['post_id'] not in seen_ids:
                seen_ids.add(post['post_id'])
                unique_posts.append(post)
        
        logger.info(f"Total unique posts from Singapore subreddits: {len(unique_posts)}")
    def scrape_all(self) -> List[Dict]:
        """Scrape all relevant Reddit posts"""
        all_posts = []
        
        # Get Singapore-specific posts (includes news subreddits)
        singapore_posts = self.scrape_singapore_subreddits()
        all_posts.extend(singapore_posts)
        
        # Get tech-related posts
        tech_posts = self.scrape_tech_subreddits()
        all_posts.extend(tech_posts)
        
        # Search for Singapore mentions
        singapore_mentions = self.search_singapore_mentions()
        all_posts.extend(singapore_mentions)
        
        # Get trending topics
        trending_posts = self.scrape_trending_topics()
        all_posts.extend(trending_posts)
        
        # Remove duplicates
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post['post_id'] not in seen_ids:
                seen_ids.add(post['post_id'])
                unique_posts.append(post)
        
        logger.info(f"Total unique Reddit posts scraped: {len(unique_posts)}")
        return unique_posts
    
    def scrape_tech_subreddits(self) -> List[Dict]:
        """Scrape technology-related subreddits"""
        tech_subreddits = [
            'technology',
            'programming',
            'artificial',
            'MachineLearning',
            'startups',
            'entrepreneur',
            'investing',
            'cryptocurrency',
            'blockchain',
            'fintech',
            'cybersecurity',
            'webdev',
            'python',
            'javascript',
            'datascience',
            'automation',
            'robotics',
            'futurology'
        ]
        
        all_posts = []
        
        for subreddit in tech_subreddits:
            # Focus on hot posts for tech subreddits
            posts = self.scrape_subreddit(subreddit, limit=20, sort_by='hot')
            all_posts.extend(posts)
        
        # Remove duplicates
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post['post_id'] not in seen_ids:
                seen_ids.add(post['post_id'])
                unique_posts.append(post)
        
        logger.info(f"Total unique posts from tech subreddits: {len(unique_posts)}")
        return unique_posts
    
    def search_singapore_mentions(self, query: str = "Singapore", limit: int = 50) -> List[Dict]:
        """Search for Singapore mentions across Reddit"""
        if not self.reddit:
            return []
        
        try:
            # Search for Singapore-related posts
            search_results = self.reddit.subreddit('all').search(
                query, 
                sort='relevance', 
                time_filter='week',
                limit=limit
            )
            
            posts = []
            for submission in search_results:
                # Filter out posts from NSFW subreddits
                if submission.over_18:
                    continue
                    
                post_time = datetime.fromtimestamp(submission.created_utc)
                content = submission.selftext if submission.selftext else submission.title
                
                post = {
                    'post_id': submission.id,
                    'title': submission.title,
                    'content': content,
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'url': f"https://reddit.com{submission.permalink}",
                    'score': submission.score,
                    'comments_count': submission.num_comments,
                    'created_at': post_time,
                    'scraped_at': datetime.now(),
                    'platform': 'reddit',
                    'subreddit': submission.subreddit.display_name
                }
                posts.append(post)
            
            logger.info(f"Found {len(posts)} Singapore-related posts from search")
            return posts
            
        except Exception as e:
            logger.error(f"Error searching for Singapore mentions: {e}")
            return []
    
    def scrape_trending_topics(self) -> List[Dict]:
        """Scrape trending topics from popular subreddits"""
        trending_subreddits = [
            'news',
            'worldnews',
            'technology',
            'business',
            'economy',
            'investing',
            'crypto',
            'stocks',
            'driving',
            'futurology'
        ]
        
        all_posts = []
        
        for subreddit in trending_subreddits:
            # Get top posts from the last week
            posts = self.scrape_subreddit(subreddit, limit=15, sort_by='top')
            all_posts.extend(posts)
        
        # Filter for high engagement posts
        high_engagement_posts = [
            post for post in all_posts 
            if post['score'] > 100 and post['comments_count'] > 20
        ]
        
        # Remove duplicates
        seen_ids = set()
        unique_posts = []
        for post in high_engagement_posts:
            if post['post_id'] not in seen_ids:
                seen_ids.add(post['post_id'])
                unique_posts.append(post)
        
        logger.info(f"Found {len(unique_posts)} trending posts")
        return unique_posts
    
    def scrape_singapore_news_only(self) -> List[Dict]:
        """Scrape only Singapore news subreddits"""
        news_subreddits = [
            'straits_times',
            'mothership', 
            'todaynews',
            'channelnewsasia',
            'singaporenews',
            'sg_news'
        ]
        
        all_posts = []
        
        for subreddit in news_subreddits:
            logger.info(f"Scraping news subreddit: r/{subreddit}")
            
            # Get comprehensive coverage from news subreddits
            hot_posts = self.scrape_subreddit(subreddit, limit=50, sort_by='hot')
            new_posts = self.scrape_subreddit(subreddit, limit=30, sort_by='new') 
            top_posts = self.scrape_subreddit(subreddit, limit=20, sort_by='top')
            
            all_posts.extend(hot_posts)
            all_posts.extend(new_posts)
            all_posts.extend(top_posts)
            
            logger.info(f"Got {len(hot_posts)} hot, {len(new_posts)} new, {len(top_posts)} top posts from r/{subreddit}")
        
        # Remove duplicates
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post['post_id'] not in seen_ids:
                seen_ids.add(post['post_id'])
                unique_posts.append(post)
        
        logger.info(f"Total unique posts from Singapore news subreddits: {len(unique_posts)}")
        return unique_posts

# Example usage and testing
if __name__ == "__main__":
    scraper = RedditScraper()
    
    if scraper.reddit:
        print("Testing Reddit scraper...")
        posts = scraper.scrape_all()
        
        print(f"Found {len(posts)} posts")
        
        # Print a few examples
        for i, post in enumerate(posts[:3]):
            print(f"\nPost {i+1}:")
            print(f"Title: {post['title']}")
            print(f"Subreddit: r/{post.get('subreddit', 'unknown')}")
            print(f"Score: {post['score']}")
            print(f"Comments: {post['comments_count']}")
            print(f"Author: {post['author']}")
            print(f"Created: {post['created_at']}")
    else:
        print("Reddit API not configured. Please check your credentials.")
# src/scrapers/hackernews_scraper.py - FIXED VERSION
"""Hacker News scraper using the official Firebase API"""

import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Simple logging setup
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HackerNewsScraper:
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TrendSense/1.0 (Singapore News Aggregator)'
        })
        
        logger.info(f"Initialized Hacker News scraper with base URL: {self.base_url}")
        
    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """Make a request to the Hacker News API"""
        try:
            url = f"{self.base_url}/{endpoint}.json"
            logger.debug(f"Making request to: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error making request to {endpoint}: {e}")
            return None
    
    def get_story_details(self, story_id: int) -> Optional[Dict]:
        """Get details for a specific story"""
        story_data = self._make_request(f"item/{story_id}")
        
        if not story_data or story_data.get('type') != 'story':
            return None
        
        # Filter for stories with good engagement
        score = story_data.get('score', 0)
        if score < 10:  # Skip stories with low engagement
            return None
        
        return {
            'post_id': str(story_id),
            'title': story_data.get('title', ''),
            'content': story_data.get('text', ''),  # Some stories have text content
            'author': story_data.get('by', ''),
            'url': story_data.get('url', f'https://news.ycombinator.com/item?id={story_id}'),
            'score': score,
            'comments_count': len(story_data.get('kids', [])),
            'created_at': datetime.fromtimestamp(story_data.get('time', 0)),
            'scraped_at': datetime.now(),
            'platform': 'hackernews'
        }
    
    def scrape_top_stories(self, limit: int = 50) -> List[Dict]:
        """Scrape top stories from Hacker News"""
        logger.info(f"Scraping top {limit} stories from Hacker News")
        
        # Get list of top story IDs
        top_stories = self._make_request("topstories")
        if not top_stories:
            logger.error("Failed to get top stories list")
            return []
        
        # Limit the number of stories to process
        story_ids = top_stories[:limit]
        logger.info(f"Processing {len(story_ids)} story IDs")
        
        # Use ThreadPoolExecutor to fetch stories in parallel
        stories = []
        with ThreadPoolExecutor(max_workers=5) as executor:  # Reduced workers to be gentler
            future_to_id = {executor.submit(self.get_story_details, story_id): story_id 
                          for story_id in story_ids}
            
            for future in as_completed(future_to_id):
                story_id = future_to_id[future]
                try:
                    story = future.result()
                    if story:
                        stories.append(story)
                        logger.debug(f"Successfully processed story {story_id}: {story['title']}")
                except Exception as e:
                    logger.error(f"Error processing story {story_id}: {e}")
        
        logger.info(f"Successfully scraped {len(stories)} stories from Hacker News")
        return stories
    
    def scrape_new_stories(self, limit: int = 100) -> List[Dict]:
        """Scrape newest stories from Hacker News"""
        logger.info(f"Scraping newest {limit} stories from Hacker News")
        
        # Get list of newest story IDs
        new_stories = self._make_request("newstories")
        if not new_stories:
            logger.error("Failed to get new stories list")
            return []
        
        # Limit the number of stories to process
        story_ids = new_stories[:limit]
        
        # Filter for recent stories (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        stories = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_id = {executor.submit(self.get_story_details, story_id): story_id 
                          for story_id in story_ids}
            
            for future in as_completed(future_to_id):
                story_id = future_to_id[future]
                try:
                    story = future.result()
                    if story and story['created_at'] > cutoff_time:
                        stories.append(story)
                except Exception as e:
                    logger.error(f"Error processing story {story_id}: {e}")
        
        logger.info(f"Successfully scraped {len(stories)} new stories from Hacker News")
        return stories
    
    def scrape_tech_stories(self, limit: int = 50) -> List[Dict]:
        """Scrape stories related to technology and startups"""
        logger.info(f"Scraping tech stories (limit: {limit})")
        
        # Get both top and new stories
        top_stories = self.scrape_top_stories(limit // 2)
        time.sleep(1)  # Brief pause between API calls
        new_stories = self.scrape_new_stories(limit // 2)
        
        # Combine all stories
        all_stories = top_stories + new_stories
        logger.info(f"Got {len(all_stories)} total stories to filter")
        
        # Keywords to identify tech/startup stories (comprehensive list)
        tech_keywords = [
            # AI/ML
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
            'neural', 'model', 'training', 'dataset', 'prediction', 'algorithm',
            'diffusion', 'transformer', 'gpt', 'llm', 'language model',
            
            # Programming languages
            'python', 'javascript', 'java', 'rust', 'go', 'c++', 'typescript',
            'php', 'ruby', 'swift', 'kotlin', 'scala', 'clojure', 'haskell',
            
            # Web technologies
            'react', 'vue', 'angular', 'node', 'npm', 'webpack', 'api', 'rest',
            'graphql', 'frontend', 'backend', 'fullstack', 'web', 'browser',
            'html', 'css', 'sass', 'tailwind', 'bootstrap',
            
            # Infrastructure/DevOps
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'cloud', 'server',
            'deploy', 'deployment', 'ci/cd', 'devops', 'infrastructure',
            'microservices', 'serverless', 'lambda', 'container',
            
            # Databases
            'database', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql',
            'redis', 'elasticsearch', 'firebase', 'sqlite',
            
            # Development tools
            'git', 'github', 'gitlab', 'vscode', 'vim', 'emacs', 'ide',
            'framework', 'library', 'open source', 'repository', 'commit',
            
            # Business/Startup
            'startup', 'funding', 'vc', 'venture capital', 'fintech', 'saas',
            'software', 'tech', 'technology', 'digital', 'platform',
            'innovation', 'silicon valley', 'ipo', 'acquisition',
            
            # Crypto/Blockchain
            'blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'web3',
            'crypto', 'defi', 'nft', 'smart contract', 'dao',
            
            # Security
            'security', 'cybersecurity', 'vulnerability', 'hack', 'breach',
            'encryption', 'privacy', 'auth', 'authentication', 'ssl', 'tls',
            
            # Mobile/Apps
            'mobile', 'app', 'ios', 'android', 'flutter', 'react native',
            'app store', 'play store', 'mobile app',
            
            # Hardware/Systems
            'chip', 'processor', 'cpu', 'gpu', 'semiconductor', 'hardware',
            'computer', 'linux', 'unix', 'macos', 'windows', 'operating system',
            
            # Data/Analytics
            'data', 'analytics', 'analysis', 'visualization', 'statistics',
            'big data', 'data science', 'etl', 'pipeline',
            
            # Emerging Tech
            'automation', 'robotics', 'iot', 'quantum', 'ar', 'vr',
            'augmented reality', 'virtual reality', 'metaverse',
            
            # Development concepts
            'programming', 'coding', 'code', 'developer', 'engineering',
            'software engineering', 'computer science', 'algorithm',
            'data structure', 'design pattern', 'architecture',
            
            # Performance/Quality
            'performance', 'optimization', 'scalability', 'testing',
            'debugging', 'profiling', 'monitoring', 'logging',
            
            # Protocols/Standards
            'protocol', 'http', 'https', 'tcp', 'ip', 'dns', 'api',
            'json', 'xml', 'yaml', 'oauth', 'jwt',
            
            # Specific tools/services
            'google', 'amazon', 'microsoft', 'meta', 'apple', 'netflix',
            'spotify', 'uber', 'airbnb', 'tesla', 'spacex',
            
            # General tech terms
            'software', 'hardware', 'firmware', 'embedded', 'iot',
            'network', 'internet', 'online', 'digital', 'electronic',
            'computer', 'technical', 'tech', 'it', 'information technology'
        ]
        
        # Programming/tech related symbols and patterns
        tech_patterns = [
            'js', 'py', 'rb', 'php', 'cpp', 'hpp', 'tsx', 'jsx',
            'derive', 'clone', 'enum', 'struct', 'class', 'function',
            'var', 'let', 'const', 'def', 'import', 'export',
            'github.com', 'gitlab.com', 'stackoverflow.com'
        ]
        
        # Combine keywords and patterns
        all_tech_terms = tech_keywords + tech_patterns
        
        # Filter stories based on tech keywords
        tech_stories = []
        for story in all_stories:
            title_lower = story['title'].lower()
            content_lower = story.get('content', '').lower()
            url_lower = story.get('url', '').lower()
            
            # Check if ANY keyword matches in title, content, or URL
            is_tech = any(
                term in title_lower or 
                term in content_lower or 
                term in url_lower 
                for term in all_tech_terms
            )
            
            # Special patterns for programming-related titles
            programming_indicators = [
                '#', '[]', '()', '{}', '<>', '//', '/*', '*/',
                'lib', 'pkg', 'mod', 'src', 'bin', 'exe',
                'v1.', 'v2.', 'v3.', '1.0', '2.0', '3.0'
            ]
            
            has_programming_pattern = any(indicator in story['title'] for indicator in programming_indicators)
            
            if is_tech or has_programming_pattern:
                tech_stories.append(story)
                logger.info(f"✅ Tech story: {story['title']}")
            else:
                logger.debug(f"❌ Not tech: {story['title']}")
        
        # Remove duplicates based on post_id
        seen_ids = set()
        unique_stories = []
        for story in tech_stories:
            if story['post_id'] not in seen_ids:
                seen_ids.add(story['post_id'])
                unique_stories.append(story)
        
        logger.info(f"Filtered to {len(unique_stories)} tech-related stories")
        return unique_stories
    
    def scrape_singapore_related(self, limit: int = 100) -> List[Dict]:
        """Scrape stories related to Singapore"""
        logger.info(f"Scraping Singapore-related stories (limit: {limit})")
        
        # Get a larger sample to find Singapore-related content
        top_stories = self.scrape_top_stories(limit // 2)
        time.sleep(1)
        new_stories = self.scrape_new_stories(limit // 2)
        
        all_stories = top_stories + new_stories
        
        # Keywords to identify Singapore-related content
        singapore_keywords = [
            'singapore', 'spore', 'sg', 'singaporean', 'singapore startup',
            'singapore tech', 'singapore fintech', 'singapore government',
            'singapore economy', 'singapore innovation', 'singapore ai',
            'singapore blockchain', 'singapore cryptocurrency', 'singapore venture',
            'singapore investment', 'singapore market', 'singapore business',
            'singapore policy', 'singapore regulation', 'singapore law',
            'singapore university', 'ntu', 'nus', 'sutd', 'smu',
            'southeast asia', 'sea', 'asean', 'asia pacific',
            'singapore-based', 'singapore company', 'singapore firm'
        ]
        
        # Filter stories based on Singapore keywords
        singapore_stories = []
        for story in all_stories:
            title_lower = story['title'].lower()
            content_lower = story.get('content', '').lower()
            
            if any(keyword in title_lower or keyword in content_lower 
                  for keyword in singapore_keywords):
                singapore_stories.append(story)
                logger.debug(f"Found Singapore story: {story['title']}")
        
        # Remove duplicates
        seen_ids = set()
        unique_stories = []
        for story in singapore_stories:
            if story['post_id'] not in seen_ids:
                seen_ids.add(story['post_id'])
                unique_stories.append(story)
        
        logger.info(f"Found {len(unique_stories)} Singapore-related stories")
        return unique_stories
    
    def scrape_all(self) -> List[Dict]:
        """Scrape all relevant stories from Hacker News"""
        logger.info("Starting comprehensive Hacker News scraping")
        
        all_stories = []
        
        # Get tech stories
        tech_stories = self.scrape_tech_stories(30)
        all_stories.extend(tech_stories)
        
        time.sleep(2)  # Pause between different scraping methods
        
        # Get Singapore-related stories
        singapore_stories = self.scrape_singapore_related(50)
        all_stories.extend(singapore_stories)
        
        # Remove duplicates
        seen_ids = set()
        unique_stories = []
        for story in all_stories:
            if story['post_id'] not in seen_ids:
                seen_ids.add(story['post_id'])
                unique_stories.append(story)
        
        logger.info(f"Total unique stories scraped from Hacker News: {len(unique_stories)}")
        return unique_stories

# Example usage and testing
if __name__ == "__main__":
    print("Testing Hacker News scraper...")
    
    scraper = HackerNewsScraper()
    
    # Test basic connectivity first
    print("\n1. Testing basic API connectivity...")
    top_stories_ids = scraper._make_request("topstories")
    if top_stories_ids:
        print(f"✅ Successfully connected! Found {len(top_stories_ids)} top story IDs")
        
        # Test getting one story
        if top_stories_ids:
            story_id = top_stories_ids[0]
            story = scraper.get_story_details(story_id)
            if story:
                print(f"✅ Successfully got story details for ID {story_id}")
                print(f"   Title: {story['title']}")
            else:
                print(f"❌ Could not get story details for ID {story_id}")
    else:
        print("❌ Could not connect to Hacker News API")
        exit(1)
    
    # Test scraping tech stories
    print("\n2. Testing tech story scraping...")
    tech_stories = scraper.scrape_tech_stories(10)
    print(f"Found {len(tech_stories)} tech stories")
    
    # Print a few examples
    for i, story in enumerate(tech_stories[:3]):
        print(f"\nStory {i+1}:")
        print(f"Title: {story['title']}")
        print(f"Score: {story['score']}")
        print(f"Comments: {story['comments_count']}")
        print(f"URL: {story['url']}")
        print(f"Created: {story['created_at']}")
    
    print(f"\n✅ Hacker News scraper test completed successfully!")
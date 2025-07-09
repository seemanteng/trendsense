# config/settings.py - FIXED VERSION
import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Force load environment variables
try:
    from dotenv import load_dotenv
    # Load from the project root
    env_path = PROJECT_ROOT / '.env'
    load_dotenv(env_path)
    print(f"Loading .env from: {env_path}")
    print(f".env exists: {env_path.exists()}")
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables from .env file will not be loaded.")

# Project paths
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = DATA_DIR / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for dir_path in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

# API Configuration - with debug info
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "TrendSense/1.0")
HACKERNEWS_API_BASE = os.getenv("HACKERNEWS_API_BASE", "https://hacker-news.firebaseio.com/v0")

# Debug: Print what we loaded (without revealing secrets)
print(f"NEWS_API_KEY loaded: {bool(NEWS_API_KEY)}")
print(f"REDDIT_CLIENT_ID loaded: {bool(REDDIT_CLIENT_ID)}")
print(f"REDDIT_CLIENT_SECRET loaded: {bool(REDDIT_CLIENT_SECRET)}")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{PROJECT_ROOT}/trendsense.db")

# App Settings
APP_NAME = os.getenv("APP_NAME", "TrendSense")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", "300"))
MAX_ARTICLES_PER_SOURCE = int(os.getenv("MAX_ARTICLES_PER_SOURCE", "100"))

# Singapore-specific settings
TARGET_REGION = os.getenv("TARGET_REGION", "Singapore")
LOCAL_NEWS_SOURCES = os.getenv("LOCAL_NEWS_SOURCES", "channelnewsasia.com,straitstimes.com,todayonline.com").split(",")

# NLP Settings
MIN_TOPIC_SIZE = 5
N_TOPICS = 20
SENTIMENT_THRESHOLD = 0.1

# Time series settings
FORECAST_DAYS = 7
MIN_DATA_POINTS = 10
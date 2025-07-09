# TrendSense 

Real-time Singapore news and social media trend analyzer with sentiment analysis and interactive visualization
<div align="center">
<img width="1424" alt="tab1" src="https://github.com/user-attachments/assets/daa8c441-8286-4e4f-b66d-9a9dfec09c18" />
</div>
<div align="center">
<img width="1420" alt="tab2" src="https://github.com/user-attachments/assets/7a3c6b43-925e-42b2-a541-8e475c7a3ed0" />
</div>
<div align="center">
<img width="1425" alt="tab3" src="https://github.com/user-attachments/assets/2dbe9b68-013e-48e8-84fe-027b6527df8c" />
</div>
<div align="center">
<img width="1412" alt="tab4" src="https://github.com/user-attachments/assets/3f2e505f-23c1-4771-b2d5-c7b0a5144bdd" />
</div>


# Features

1. Multi-Source Data Collection

- Hacker News trending tech stories
- NewsAPI for Singapore-focused articles
- Reddit posts from Singapore communities
- Configurable RSS feed integration


2. Advanced NLP Analysis

- Real-time sentiment analysis (TextBlob + VADER)
- Topic clustering and trend detection
- Singapore-specific content filtering
- Tech industry focus with smart keyword matching


3. Interactive Dashboard

- Live data visualization with Plotly
- Sentiment trends over time
- Source distribution analytics
- Story popularity metrics


4. Production Ready

- SQLAlchemy database integration
- Automated scheduling and data collection
- Comprehensive logging and error handling
- Modular, scalable architecture

5. Tech Stack
- Backend: Python 3.8+, SQLAlchemy, SQLite
- Frontend: Streamlit, Plotly, HTML/CSS
- APIs: NewsAPI, Reddit API (PRAW), Hacker News API
- NLP: TextBlob, VADER Sentiment, spaCy
- Data Processing: Pandas, NumPy
- Deployment: Docker-ready, environment-based configuration

# Quick Start
Prerequisites 
- Python 3.8 or higher
- Git
- Internet connection for API access

Clone and Setup
<pre>
bash# Clone the repository
git clone https://github.com/seemanteng/trendsense.git
cd trendsense
</pre>

Create virtual environment (OUTSIDE project directory)
<pre>
cd ..
python -m venv trendsense_env
source trendsense_env/bin/activate  # On Windows: trendsense_env\Scripts\activate
</pre>

Install dependencies
<pre>
cd trendsense
pip install -r requirements.txt
</pre>

Download spaCy language model
<pre>
python -m spacy download en_core_web_sm
</pre>

Configuration
<pre>
bash# Copy environment template
cp .env.example .env
</pre>

Edit .env with your API keys 
<pre>
nano .env  # or use your preferred editor
</pre>
    
3. Initialize Database
<pre>
bashpython scripts/setup_db.py
</pre>

5. Run the Application
<pre>
bash# Start data collection (in one terminal)
python scripts/run_scraper.py
</pre>

6. Launch dashboard (in another terminal)
<pre>
streamlit run dashboard/app.py
Visit http://localhost:8501 to access the dashboard.
</pre>

# API Setup
Required APIs
1. NewsAPI (Required)
- Visit newsapi.org
- Sign up for a free account
- Copy your API key to .env file

2. Reddit API (Optional but Recommended)
- Go to reddit.com/prefs/apps
- Click "Create App"
- Choose "script" type
- Fill in your details:
<pre>
Name: TrendSense
Description: News trend analyzer
Redirect URI: http://localhost:8080
</pre>

Add credentials to .env:
<pre>
envREDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=TrendSense/1.0
</pre>
3. Hacker News (No Setup Required)
Uses public API - no authentication needed!

# Project Structure
<pre>
trendsense/
├── config/                 # Configuration files
│   ├── settings.py         # Main app configuration
│   └── database.py         # Database setup
├── src/                    # Core application code
│   ├── scrapers/           # Data collection modules
│   │   ├── news_scraper.py     # NewsAPI + RSS integration
│   │   ├── reddit_scraper.py   # Reddit data collection
│   │   └── hackernews_scraper.py # Hacker News integration
│   ├── nlp/                # Natural language processing
│   │   ├── sentiment_analysis.py # Sentiment analysis pipeline
│   │   └── topic_clustering.py   # Topic detection
│   ├── data/               # Database models and management
│   │   ├── models.py           # SQLAlchemy models
│   │   └── database_manager.py # Database operations
│   └── utils/              # Utility functions
│       ├── logger.py           # Logging configuration
│       └── helpers.py          # Helper functions
├── dashboard/              # Streamlit web interface
│   ├── app.py              # Main dashboard application
│   └── components/         # Dashboard components
├── scripts/                # Automation and setup scripts
│   ├── setup_db.py         # Database initialization
│   ├── run_scraper.py      # Main data collection script
│   └── scheduler.py        # Automated scheduling
├── data/                   # Data storage
│   ├── raw/                # Raw scraped data
│   ├── processed/          # Processed datasets
│   └── models/             # ML model storage
├── tests/                  # Test suite
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
</pre>

# Scrape latest tech stories
<pre>
scraper = HackerNewsScraper()
stories = scraper.scrape_tech_stories(limit=20)
</pre>

# Analyze sentiment
<pre>
analyzer = SentimentAnalyzer()
for story in stories:
    sentiment = analyzer.analyze_text(story['title'])
    print(f"{story['title']}: {sentiment['label']} ({sentiment['score']:.2f})")
Custom Subreddit Monitoring
pythonfrom src.scrapers.reddit_scraper import RedditScraper

scraper = RedditScraper()
custom_subreddits = ['singapore', 'technology', 'startups']
posts = scraper.scrape_custom_list(custom_subreddits, limit_per_sub=50)
Dashboard Integration
The Streamlit dashboard provides:

Real-time metrics: Story counts, sentiment averages, source distribution
Interactive charts: Sentiment trends, popularity over time
Data filtering: By source, time range, sentiment
Live updates: Click "Scrape New Data" for fresh content
</pre>

# Configuration
Environment Variables
<pre>
env# API Configuration
NEWS_API_KEY=your_newsapi_key
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=TrendSense/1.0
</pre>

# Database
<pre>
DATABASE_URL=sqlite:///trendsense.db
</pre>

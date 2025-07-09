# dashboard/app.py - FULL STREAMLIT VERSION
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.data.database_manager import DatabaseManager
    from src.data.models import SocialPost, NewsArticle
    from src.scrapers.hackernews_scraper import HackerNewsScraper
    from src.nlp.sentiment_analysis import SentimentAnalyzer
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="TrendSense",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def init_components():
    try:
        db_manager = DatabaseManager()
        sentiment_analyzer = SentimentAnalyzer()
        hn_scraper = HackerNewsScraper()
        return db_manager, sentiment_analyzer, hn_scraper
    except Exception as e:
        st.error(f"Error initializing components: {e}")
        return None, None, None

def load_data(db_manager, hours=24):
    """Load data from database"""
    try:
        # Get social posts (Hacker News)
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        posts = db_manager.session.query(SocialPost).filter(
            SocialPost.created_at >= cutoff_time
        ).all()
        
        # Convert to DataFrame
        if posts:
            data = []
            for post in posts:
                data.append({
                    'title': post.title,
                    'platform': post.platform,
                    'score': post.score,
                    'comments': post.comments_count,
                    'sentiment_score': post.sentiment_score,
                    'sentiment_label': post.sentiment_label,
                    'created_at': post.created_at,
                    'author': post.author,
                    'url': post.url
                })
            return pd.DataFrame(data)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def scrape_live_data():
    """Scrape and analyze new data from all sources"""
    try:
        db_manager, sentiment_analyzer, hn_scraper = init_components()
        
        if not all([db_manager, sentiment_analyzer, hn_scraper]):
            return False
        
        total_saved = 0
        
        # Scrape Hacker News
        with st.spinner("Scraping latest stories from Hacker News..."):
            hn_stories = hn_scraper.scrape_tech_stories(10)
            
            if hn_stories:
                # Analyze sentiment
                for story in hn_stories:
                    sentiment = sentiment_analyzer.analyze_text(story['title'] + ' ' + story.get('content', ''))
                    story['sentiment_score'] = sentiment['score']
                    story['sentiment_label'] = sentiment['label']
                
                saved_hn = db_manager.save_social_posts(hn_stories)
                total_saved += saved_hn
                st.success(f"✅ Hacker News: {saved_hn} stories")
        
        # Scrape News Articles
        try:
            from src.scrapers.news_scraper import NewsScraper
            news_scraper = NewsScraper()
            
            with st.spinner("Scraping news articles..."):
                articles = news_scraper.scrape_all()
                
                if articles:
                    # Analyze sentiment
                    for article in articles:
                        sentiment = sentiment_analyzer.analyze_text(article['title'] + ' ' + article.get('content', ''))
                        article['sentiment_score'] = sentiment['score']
                        article['sentiment_label'] = sentiment['label']
                    
                    saved_news = db_manager.save_articles(articles)
                    total_saved += saved_news
                    st.success(f"✅ News Articles: {saved_news} articles")
                else:
                    st.warning("⚠️ No news articles found")
                    
        except Exception as e:
            st.warning(f"⚠️ News scraping failed: {e}")
        
        # Scrape Reddit (if configured)
        try:
            from src.scrapers.reddit_scraper import RedditScraper
            reddit_scraper = RedditScraper()
            
            if reddit_scraper.reddit:
                with st.spinner("Scraping Reddit posts..."):
                    reddit_posts = reddit_scraper.scrape_singapore_subreddits()
                    
                    if reddit_posts:
                        # Analyze sentiment
                        for post in reddit_posts:
                            sentiment = sentiment_analyzer.analyze_text(post['title'] + ' ' + post.get('content', ''))
                            post['sentiment_score'] = sentiment['score']
                            post['sentiment_label'] = sentiment['label']
                        
                        saved_reddit = db_manager.save_social_posts(reddit_posts)
                        total_saved += saved_reddit
                        st.success(f"✅ Reddit: {saved_reddit} posts")
                    else:
                        st.warning("⚠️ No Reddit posts found")
            else:
                st.info("ℹ️ Reddit not configured - skipping")
                
        except Exception as e:
            st.warning(f"⚠️ Reddit scraping failed: {e}")
        
        if total_saved > 0:
            st.success(f"🎉 Total: {total_saved} new items scraped and analyzed!")
            return True
        else:
            st.warning("No new data found from any source")
            return False
        
    except Exception as e:
        st.error(f"Error scraping data: {e}")
        return False

def main():
    # Header
    st.title("📰 TrendSense Dashboard")
    st.markdown("*Real-time tech news and trend analysis*")
    
    # Initialize components
    db_manager, sentiment_analyzer, hn_scraper = init_components()
    
    if not all([db_manager, sentiment_analyzer, hn_scraper]):
        st.error("Failed to initialize components. Please check your setup.")
        return
    
    # Sidebar controls
    st.sidebar.title("⚙️ Controls")
    
    # Scrape button
    if st.sidebar.button("🔄 Scrape New Data", type="primary"):
        scrape_live_data()
        st.rerun()
    
    # Time range selector
    time_options = {
        "Last 24 hours": 24,
        "Last 7 days": 168,
        "Last 30 days": 720
    }
    
    selected_time = st.sidebar.selectbox("📅 Time Range", list(time_options.keys()))
    hours = time_options[selected_time]
    
    # Load data
    df = load_data(db_manager, hours)
    
    if df.empty:
        st.warning("🔍 No data found. Click 'Scrape New Data' to get started!")
        
        # Show sample scraping
        if st.button("🚀 Get Sample Data"):
            if scrape_live_data():
                st.rerun()
        return
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Stories", len(df))
    
    with col2:
        avg_score = df['score'].mean() if not df.empty else 0
        st.metric("⭐ Avg Score", f"{avg_score:.1f}")
    
    with col3:
        platforms = df['platform'].nunique() if not df.empty else 0
        st.metric("🌐 Platforms", platforms)
    
    with col4:
        avg_sentiment = df['sentiment_score'].mean() if not df.empty and 'sentiment_score' in df.columns else 0
        sentiment_emoji = "😊" if avg_sentiment > 0.1 else "😐" if avg_sentiment > -0.1 else "😟"
        st.metric("💭 Avg Sentiment", f"{sentiment_emoji} {avg_sentiment:.2f}")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📰 Stories", "💭 Sentiment", "📊 Analytics"])
    
    with tab1:
        st.header("📈 Trending Overview")
        
        if not df.empty:
            # Time series of stories
            df['date'] = pd.to_datetime(df['created_at']).dt.date
            daily_counts = df.groupby('date').size().reset_index(name='count')
            
            fig_timeline = px.line(daily_counts, x='date', y='count', 
                                 title="Stories Over Time",
                                 markers=True)
            fig_timeline.update_layout(height=400)
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Platform distribution
            col1, col2 = st.columns(2)
            
            with col1:
                platform_counts = df['platform'].value_counts()
                fig_platform = px.pie(values=platform_counts.values, 
                                     names=platform_counts.index,
                                     title="Stories by Platform")
                st.plotly_chart(fig_platform, use_container_width=True)
            
            with col2:
                # Score distribution
                fig_score = px.histogram(df, x='score', nbins=20, 
                                       title="Score Distribution")
                st.plotly_chart(fig_score, use_container_width=True)
    
    with tab2:
        st.header("📰 Latest Stories")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            platform_filter = st.selectbox("Platform", ["All"] + list(df['platform'].unique()))
        with col2:
            min_score = st.slider("Minimum Score", 0, int(df['score'].max()), 0)
        
        # Filter data
        filtered_df = df.copy()
        if platform_filter != "All":
            filtered_df = filtered_df[filtered_df['platform'] == platform_filter]
        filtered_df = filtered_df[filtered_df['score'] >= min_score]
        
        # Sort by score
        filtered_df = filtered_df.sort_values('score', ascending=False)
        
        # Display stories
        for idx, story in filtered_df.head(20).iterrows():
            with st.expander(f"⭐ {story['score']} | {story['title']}", expanded=False):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Platform:** {story['platform']}")
                    st.write(f"**Author:** {story['author']}")
                    if story.get('url'):
                        st.write(f"**URL:** {story['url']}")
                
                with col2:
                    st.write(f"**Score:** {story['score']}")
                    st.write(f"**Comments:** {story['comments']}")
                
                with col3:
                    if story.get('sentiment_label'):
                        sentiment_color = {
                            'positive': '🟢',
                            'negative': '🔴', 
                            'neutral': '🟡'
                        }.get(story['sentiment_label'], '⚪')
                        st.write(f"**Sentiment:** {sentiment_color} {story['sentiment_label']}")
                        if story.get('sentiment_score'):
                            st.write(f"**Score:** {story['sentiment_score']:.2f}")
    
    with tab3:
        st.header("💭 Sentiment Analysis")
        
        if not df.empty and 'sentiment_score' in df.columns:
            # Sentiment over time
            df['hour'] = pd.to_datetime(df['created_at']).dt.hour
            hourly_sentiment = df.groupby('hour')['sentiment_score'].mean().reset_index()
            
            fig_sentiment = px.line(hourly_sentiment, x='hour', y='sentiment_score',
                                  title="Average Sentiment by Hour",
                                  markers=True)
            fig_sentiment.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig_sentiment, use_container_width=True)
            
            # Sentiment distribution
            col1, col2 = st.columns(2)
            
            with col1:
                if 'sentiment_label' in df.columns:
                    sentiment_counts = df['sentiment_label'].value_counts()
                    fig_sent_dist = px.pie(values=sentiment_counts.values,
                                         names=sentiment_counts.index,
                                         title="Sentiment Distribution",
                                         color_discrete_map={
                                             'positive': '#00ff00',
                                             'negative': '#ff0000',
                                             'neutral': '#ffff00'
                                         })
                    st.plotly_chart(fig_sent_dist, use_container_width=True)
            
            with col2:
                # Sentiment vs Score correlation
                fig_corr = px.scatter(df, x='sentiment_score', y='score',
                                    title="Sentiment vs Popularity",
                                    trendline="ols")
                st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("No sentiment data available. Scrape some data first!")
    
    with tab4:
        st.header("📊 Advanced Analytics")
        
        if not df.empty:
            # Top authors
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏆 Top Authors")
                author_stats = df.groupby('author').agg({
                    'score': ['count', 'mean', 'sum']
                }).round(2)
                author_stats.columns = ['Stories', 'Avg Score', 'Total Score']
                author_stats = author_stats.sort_values('Total Score', ascending=False)
                st.dataframe(author_stats.head(10))
            
            with col2:
                st.subheader("🔥 Hottest Stories")
                hot_stories = df.nlargest(10, 'score')[['title', 'score', 'platform']]
                st.dataframe(hot_stories)
            
            # Word cloud placeholder
            st.subheader("☁️ Trending Topics")
            st.info("Word cloud visualization coming soon! This would show trending keywords from story titles.")
            
            # Raw data
            with st.expander("🔍 Raw Data"):
                st.dataframe(df)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>🚀 <strong>TrendSense</strong> - Real-time tech news analysis | 
            Built with Streamlit & Python | 
            Data from Hacker News & Reddit</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
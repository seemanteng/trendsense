import sys
from pathlib import Path
from typing import Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from textblob import TextBlob
except ImportError:
    print("TextBlob not installed. Please run: pip install textblob")
    TextBlob = None

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    print("VADER Sentiment not installed. Please run: pip install vaderSentiment")
    SentimentIntensityAnalyzer = None

try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer() if SentimentIntensityAnalyzer else None
        
    def analyze_text(self, text: str) -> Dict:
        """Analyze sentiment of text using multiple methods"""
        if not text:
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
        
        scores = []
        
        # VADER Sentiment
        if self.vader_analyzer:
            vader_scores = self.vader_analyzer.polarity_scores(text)
            scores.append(vader_scores['compound'])
        
        # TextBlob sentiment
        if TextBlob:
            blob = TextBlob(text)
            scores.append(blob.sentiment.polarity)
        
        # Calculate average if we have scores
        if scores:
            avg_score = sum(scores) / len(scores)
        else:
            # Fallback simple sentiment
            avg_score = self._simple_sentiment(text)
        
        # Determine label
        if avg_score > 0.1:
            label = 'positive'
        elif avg_score < -0.1:
            label = 'negative'
        else:
            label = 'neutral'
        
        confidence = abs(avg_score)
        
        return {
            'score': round(avg_score, 3),
            'label': label,
            'confidence': round(confidence, 3)
        }
    
    def _simple_sentiment(self, text: str) -> float:
        """Simple rule-based sentiment analysis as fallback"""
        positive_words = ['good', 'great', 'excellent', 'awesome', 'amazing', 'love', 'like', 'best', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disgusting', 'disappointing', 'sad', 'angry']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
        
        sentiment_score = (pos_count - neg_count) / total_words
        return max(-1.0, min(1.0, sentiment_score))
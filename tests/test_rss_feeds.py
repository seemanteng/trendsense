# test_rss_feeds.py - Test RSS feeds
import feedparser
import requests

def test_rss_feed(url, name):
    """Test if an RSS feed is working"""
    print(f"\nTesting {name}: {url}")
    
    try:
        # Try with requests first
        response = requests.get(url, timeout=10)
        print(f"  HTTP Status: {response.status_code}")
        
        # Try with feedparser
        feed = feedparser.parse(url)
        
        if feed.bozo:
            print(f"  ❌ Feed parsing error: {feed.bozo_exception}")
        else:
            print(f"  ✅ Feed parsed successfully")
            print(f"  ✅ Found {len(feed.entries)} entries")
            
            if feed.entries:
                first_entry = feed.entries[0]
                print(f"  📰 Latest: {first_entry.get('title', 'No title')}")
                print(f"  🔗 Link: {first_entry.get('link', 'No link')}")
        
        return len(feed.entries) > 0
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

# Test current RSS feeds
feeds_to_test = [
    ("https://www.channelnewsasia.com/rss-feeds", "Channel NewsAsia"),
    ("https://www.straitstimes.com/rss", "Straits Times"),
    ("https://www.todayonline.com/rss", "Today Online"),
    
    # Alternative feeds to try
    ("https://www.channelnewsasia.com/rss/8396", "CNA Singapore"),
    ("https://www.channelnewsasia.com/rss/8395", "CNA Business"),
    ("https://feeds.bbci.co.uk/news/technology/rss.xml", "BBC Tech"),
    ("http://feeds.reuters.com/reuters/technologyNews", "Reuters Tech"),
    ("https://techcrunch.com/feed/", "TechCrunch"),
]

print("Testing RSS Feeds...")
working_feeds = []

for url, name in feeds_to_test:
    if test_rss_feed(url, name):
        working_feeds.append((url, name))

print(f"\n✅ Working feeds found: {len(working_feeds)}")
for url, name in working_feeds:
    print(f"  - {name}: {url}")
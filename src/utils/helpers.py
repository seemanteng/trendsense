import re
from urllib.parse import urlparse
from typing import Optional

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove HTML tags if any
    text = re.sub(r'<[^>]+>', '', text)
    return text

def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    if not url:
        return ""
    try:
        return urlparse(url).netloc.replace('www.', '')
    except:
        return ""

def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
"""
Utilities for extracting and formatting references.
"""

import re
from typing import List, Dict, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


def clean_url(url: str) -> str:
    """
    Clean and normalize a URL.

    Args:
        url: URL to clean

    Returns:
        Cleaned URL
    """
    # Remove tracking parameters
    url = re.sub(r'[?&]utm_[^&]*', '', url)
    url = re.sub(r'[?&]ref=[^&]*', '', url)

    # Remove trailing slashes
    url = url.rstrip('/')

    # Fix double question marks
    url = re.sub(r'\?+', '?', url)

    # Remove trailing ? or &
    url = url.rstrip('?&')

    return url


def extract_urls(text: str) -> List[str]:
    """
    Extract all URLs from text.

    Args:
        text: Text to search for URLs

    Returns:
        List of unique URLs found in the text
    """
    # Pattern to match URLs
    url_pattern = r'https?://[^\s<>"{}|\\^\[\]`]+'

    urls = re.findall(url_pattern, text)

    # Clean and deduplicate
    cleaned_urls = [clean_url(url) for url in urls]
    return list(set(cleaned_urls))


def extract_youtube_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various YouTube URL formats.

    Args:
        url: YouTube URL

    Returns:
        Video ID or None if not found
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def fetch_page_title(url: str, timeout: int = 5) -> Optional[str]:
    """
    Fetch the title of a webpage.

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds

    Returns:
        Page title or None if failed
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')

        if title_tag:
            return title_tag.text.strip()

    except Exception as e:
        print(f"Failed to fetch title for {url}: {e}")

    return None


def format_reference(url: str, title: str = None, note: str = None) -> Dict[str, str]:
    """
    Format a reference dictionary for Jekyll frontmatter.

    Args:
        url: Reference URL
        title: Reference title (will fetch if not provided)
        note: Optional note about the reference

    Returns:
        Reference dictionary
    """
    url = clean_url(url)

    # Try to fetch title if not provided
    if not title:
        title = fetch_page_title(url)

    # Fallback to URL domain if title fetch fails
    if not title:
        parsed = urlparse(url)
        title = f"Link - {parsed.netloc}"

    ref = {
        'title': title,
        'url': url
    }

    if note:
        ref['note'] = note

    return ref


def create_references_from_urls(urls: List[str], fetch_titles: bool = True) -> List[Dict[str, str]]:
    """
    Create a list of reference dictionaries from URLs.

    Args:
        urls: List of URLs
        fetch_titles: Whether to fetch page titles (can be slow)

    Returns:
        List of reference dictionaries
    """
    references = []

    for url in urls:
        url = clean_url(url)

        title = None
        if fetch_titles:
            print(f"Fetching title for {url}...")
            title = fetch_page_title(url)

        ref = format_reference(url, title)
        references.append(ref)

    return references


def detect_youtube_urls(text: str) -> List[Dict[str, str]]:
    """
    Detect YouTube URLs in text and extract video information.

    Args:
        text: Text to search

    Returns:
        List of dictionaries with 'url', 'video_id', and optionally 'timestamp'
    """
    urls = extract_urls(text)
    youtube_videos = []

    for url in urls:
        if 'youtube.com' in url or 'youtu.be' in url:
            video_id = extract_youtube_id(url)
            if video_id:
                video_info = {
                    'url': url,
                    'video_id': video_id
                }

                # Try to extract timestamp (t= or start= parameter)
                timestamp_match = re.search(r'[?&](?:t|start)=(\d+)', url)
                if timestamp_match:
                    video_info['timestamp'] = int(timestamp_match.group(1))

                youtube_videos.append(video_info)

    return youtube_videos

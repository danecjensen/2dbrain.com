"""
Utilities for working with Markdown and Jekyll frontmatter.
"""

import re
from datetime import datetime
from typing import Dict, List, Any
import frontmatter


def sanitize_title(title: str) -> str:
    """
    Sanitize a title for use in filenames.

    Args:
        title: The title to sanitize

    Returns:
        A sanitized version suitable for filenames
    """
    # Convert to lowercase
    title = title.lower()
    # Replace spaces with hyphens
    title = re.sub(r'\s+', '-', title)
    # Remove special characters
    title = re.sub(r'[^a-z0-9\-]', '', title)
    # Remove multiple consecutive hyphens
    title = re.sub(r'-+', '-', title)
    # Remove leading/trailing hyphens
    title = title.strip('-')
    return title


def generate_filename(title: str, date: datetime = None) -> str:
    """
    Generate a Jekyll-style filename for a blog post.

    Args:
        title: The post title
        date: The post date (defaults to today)

    Returns:
        A filename in the format YYYY-MM-DD-title.md
    """
    if date is None:
        date = datetime.now()

    date_str = date.strftime('%Y-%m-%d')
    slug = sanitize_title(title)
    return f"{date_str}-{slug}.md"


def format_frontmatter(
    title: str,
    date: datetime = None,
    tags: List[str] = None,
    image: str = None,
    references: List[Dict[str, str]] = None,
    layout: str = "post",
    **kwargs
) -> Dict[str, Any]:
    """
    Create a frontmatter dictionary for a Jekyll post.

    Args:
        title: Post title
        date: Post date (defaults to today)
        tags: List of tags
        image: Path to header image
        references: List of reference dictionaries
        layout: Layout to use (default: "post")
        **kwargs: Additional frontmatter fields

    Returns:
        A dictionary suitable for use with python-frontmatter
    """
    if date is None:
        date = datetime.now()

    fm = {
        'layout': layout,
        'title': title,
        'date': date.strftime('%Y-%m-%d'),
        'tags': tags or [],
    }

    if image:
        fm['image'] = image

    if references:
        fm['references'] = references

    # Add any additional fields
    fm.update(kwargs)

    return fm


def create_post_with_frontmatter(content: str, frontmatter_dict: Dict[str, Any]) -> str:
    """
    Create a complete post file with frontmatter and content.

    Args:
        content: The Markdown content
        frontmatter_dict: Dictionary of frontmatter fields

    Returns:
        Complete post content with frontmatter
    """
    post = frontmatter.Post(content)
    post.metadata = frontmatter_dict
    return frontmatter.dumps(post)


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from Markdown text.

    Args:
        text: Markdown text

    Returns:
        List of dictionaries with 'language' and 'code' keys
    """
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)

    blocks = []
    for lang, code in matches:
        blocks.append({
            'language': lang or 'text',
            'code': code.strip()
        })

    return blocks


def format_youtube_embed(video_id: str, start: int = None, end: int = None, caption: str = None) -> str:
    """
    Generate a YouTube embed include tag for Jekyll.

    Args:
        video_id: YouTube video ID
        start: Start time in seconds
        end: End time in seconds
        caption: Optional caption

    Returns:
        Jekyll include tag for YouTube embed
    """
    parts = [f'id="{video_id}"']

    if start is not None:
        parts.append(f'start="{start}"')

    if end is not None:
        parts.append(f'end="{end}"')

    if caption:
        parts.append(f'caption="{caption}"')

    return "{% include youtube.html " + " ".join(parts) + " %}"

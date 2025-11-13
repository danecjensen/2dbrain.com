#!/usr/bin/env python3
"""
Convert LLM chat conversations (ChatGPT, Claude, Grok) to Jekyll blog posts.

Usage:
    python chat_to_post.py input.json
    python chat_to_post.py input.json --title "My Post" --tags ai,chatgpt
    python chat_to_post.py input.txt --format plain --fetch-titles
"""

import sys
import os
import json
import click
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent))

from utils.llm_parsers import auto_detect_and_parse, Conversation
from utils.markdown_utils import (
    format_frontmatter,
    generate_filename,
    create_post_with_frontmatter,
    format_youtube_embed
)
from utils.reference_utils import (
    extract_urls,
    create_references_from_urls,
    detect_youtube_urls
)


def conversation_to_post_content(
    conversation: Conversation,
    include_full_conversation: bool = False,
    extract_insights: bool = True
) -> str:
    """
    Convert a conversation to blog post content.

    Args:
        conversation: Parsed conversation
        include_full_conversation: Include full chat transcript
        extract_insights: Try to extract key insights

    Returns:
        Markdown content for the post
    """
    lines = []

    if extract_insights:
        # Add a summary section
        lines.append("## Summary\n")
        lines.append("*Key insights from the conversation:*\n")
        lines.append("- TODO: Add key insights here\n")
        lines.append("- TODO: Add main takeaways\n")
        lines.append("")

    if include_full_conversation:
        lines.append("## Conversation\n")
        lines.append(conversation.to_markdown())
    else:
        # Just include assistant responses as the main content
        lines.append("## Key Points\n")
        for i, msg in enumerate(conversation.get_assistant_messages(), 1):
            lines.append(f"### Point {i}\n")
            lines.append(f"{msg.content}\n")

    return '\n'.join(lines)


def process_conversation_file(
    filepath: str,
    title: str = None,
    tags: list = None,
    output_dir: str = None,
    fetch_titles: bool = False,
    include_full_conversation: bool = False,
    interactive: bool = True
) -> str:
    """
    Process a conversation file and create a blog post.

    Args:
        filepath: Path to the conversation file
        title: Optional title (will use conversation title if not provided)
        tags: List of tags
        output_dir: Output directory for the post
        fetch_titles: Whether to fetch page titles for URLs
        include_full_conversation: Include full chat transcript
        interactive: Prompt for edits before saving

    Returns:
        Path to the created post file
    """
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse the conversation
    click.echo(f"Parsing conversation from {filepath}...")
    conversation = auto_detect_and_parse(content)

    if not conversation.messages:
        raise ValueError("No messages found in the conversation file")

    click.echo(f"Found {len(conversation.messages)} messages")

    # Use provided title or conversation title
    post_title = title or conversation.title

    # Interactive title confirmation
    if interactive and not title:
        new_title = click.prompt("Post title", default=post_title)
        if new_title:
            post_title = new_title

    # Extract URLs from conversation
    all_text = ' '.join(msg.content for msg in conversation.messages)
    urls = extract_urls(all_text)

    click.echo(f"Found {len(urls)} URLs in conversation")

    # Create references
    references = []
    if urls:
        if fetch_titles:
            click.echo("Fetching page titles (this may take a moment)...")
        references = create_references_from_urls(urls, fetch_titles=fetch_titles)

    # Interactive reference editing
    if interactive and references:
        click.echo(f"\nFound {len(references)} references:")
        for i, ref in enumerate(references, 1):
            click.echo(f"  {i}. {ref['title']} - {ref['url']}")

        if click.confirm("\nEdit references?", default=False):
            # TODO: Implement interactive reference editing
            click.echo("Reference editing not yet implemented. You can edit the file after creation.")

    # Detect YouTube videos
    youtube_videos = detect_youtube_urls(all_text)
    if youtube_videos:
        click.echo(f"Found {len(youtube_videos)} YouTube video(s)")

    # Get or prompt for tags
    if tags is None and interactive:
        tags_input = click.prompt("Tags (comma-separated)", default="ai,llm,quick-insights")
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
    elif tags is None:
        tags = []

    # Generate post content
    post_content = conversation_to_post_content(
        conversation,
        include_full_conversation=include_full_conversation,
        extract_insights=True
    )

    # Add YouTube embeds section if found
    if youtube_videos:
        post_content += "\n\n## Related Videos\n\n"
        for video in youtube_videos:
            embed_code = format_youtube_embed(
                video['video_id'],
                start=video.get('timestamp')
            )
            post_content += f"{embed_code}\n\n"

    # Create frontmatter
    frontmatter = format_frontmatter(
        title=post_title,
        date=datetime.now(),
        tags=tags,
        references=references if references else None
    )

    # Create complete post
    full_post = create_post_with_frontmatter(post_content, frontmatter)

    # Preview
    if interactive:
        click.echo("\n" + "="*60)
        click.echo("POST PREVIEW")
        click.echo("="*60)
        click.echo(full_post[:500] + "..." if len(full_post) > 500 else full_post)
        click.echo("="*60 + "\n")

        if not click.confirm("Create this post?", default=True):
            click.echo("Cancelled.")
            return None

    # Determine output path
    if output_dir is None:
        # Default to _posts directory
        script_dir = Path(__file__).parent.parent
        output_dir = script_dir / "_posts"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    filename = generate_filename(post_title)
    output_path = output_dir / filename

    # Check if file exists
    if output_path.exists():
        if not click.confirm(f"File {filename} already exists. Overwrite?", default=False):
            # Generate alternative filename
            timestamp = datetime.now().strftime('%H%M%S')
            filename = generate_filename(f"{post_title}-{timestamp}")
            output_path = output_dir / filename

    # Write the file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_post)

    click.echo(f"\n✓ Post created: {output_path}")

    return str(output_path)


@click.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--title', '-t', help='Post title (uses conversation title if not provided)')
@click.option('--tags', '-g', help='Comma-separated tags')
@click.option('--output-dir', '-o', help='Output directory (default: _posts)')
@click.option('--fetch-titles/--no-fetch-titles', default=False,
              help='Fetch page titles for URLs (slower but more accurate)')
@click.option('--full-conversation/--key-points', default=False,
              help='Include full conversation or just key points')
@click.option('--interactive/--no-interactive', default=True,
              help='Interactive mode with prompts')
def main(filepath, title, tags, output_dir, fetch_titles, full_conversation, interactive):
    """
    Convert an LLM chat conversation to a Jekyll blog post.

    Supports ChatGPT, Claude, and Grok conversation exports in JSON or plain text format.

    Examples:

        # Basic usage
        python chat_to_post.py conversation.json

        # Specify title and tags
        python chat_to_post.py chat.json --title "My Insights" --tags ai,productivity

        # Non-interactive mode
        python chat_to_post.py chat.txt --no-interactive --fetch-titles

        # Include full conversation
        python chat_to_post.py chat.json --full-conversation
    """
    try:
        # Parse tags if provided
        tag_list = [tag.strip() for tag in tags.split(',')] if tags else None

        # Process the file
        output_path = process_conversation_file(
            filepath=filepath,
            title=title,
            tags=tag_list,
            output_dir=output_dir,
            fetch_titles=fetch_titles,
            include_full_conversation=full_conversation,
            interactive=interactive
        )

        if output_path:
            click.echo("\n✓ Done! You can now:")
            click.echo(f"  1. Edit the post: {output_path}")
            click.echo(f"  2. Preview with Jekyll: bundle exec jekyll serve")
            click.echo(f"  3. Commit and push to publish")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if interactive:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

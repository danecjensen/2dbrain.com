#!/usr/bin/env python3
"""
Add a reference to an existing blog post.

Usage:
    python add_reference.py post.md https://example.com/article
    python add_reference.py post.md https://example.com --title "Article Title"
"""

import sys
import click
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import frontmatter
from utils.reference_utils import format_reference


@click.command()
@click.argument('post_file', type=click.Path(exists=True))
@click.argument('url')
@click.option('--title', '-t', help='Reference title (will fetch if not provided)')
@click.option('--note', '-n', help='Optional note about the reference')
@click.option('--fetch/--no-fetch', default=True, help='Fetch page title')
def main(post_file, url, title, note, fetch):
    """
    Add a reference to an existing blog post.

    Examples:

        # Add reference with auto-fetched title
        python add_reference.py post.md https://example.com/article

        # Add reference with custom title
        python add_reference.py post.md https://example.com --title "My Article"

        # Add reference with note
        python add_reference.py post.md https://example.com --note "Good overview"
    """
    # Read the post
    with open(post_file, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

    # Create reference
    click.echo(f"Creating reference for: {url}")
    ref = format_reference(url, title=title, note=note)

    if not title and fetch:
        click.echo(f"Fetched title: {ref['title']}")

    # Add to post frontmatter
    if 'references' not in post.metadata:
        post.metadata['references'] = []

    # Check if URL already exists
    existing_urls = [r['url'] for r in post.metadata['references']]
    if url in existing_urls:
        click.echo(f"Warning: URL already exists in references")
        if not click.confirm("Add anyway?", default=False):
            return

    post.metadata['references'].append(ref)

    # Write back
    with open(post_file, 'w', encoding='utf-8') as f:
        f.write(frontmatter.dumps(post))

    click.echo(f"✓ Added reference to {post_file}")
    click.echo(f"  Total references: {len(post.metadata['references'])}")


if __name__ == '__main__':
    main()

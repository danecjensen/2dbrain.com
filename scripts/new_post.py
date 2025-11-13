#!/usr/bin/env python3
"""
Create a new blog post with a template.

Usage:
    python new_post.py
    python new_post.py --title "My Post" --tags ai,productivity
"""

import sys
import click
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from utils.markdown_utils import (
    format_frontmatter,
    generate_filename,
    create_post_with_frontmatter
)


POST_TEMPLATE = """Write your post content here.

## Section 1

Your content...

## Section 2

More content...
"""


@click.command()
@click.option('--title', '-t', prompt='Post title', help='Post title')
@click.option('--tags', '-g', prompt='Tags (comma-separated)',
              default='quick-insights', help='Comma-separated tags')
@click.option('--image', '-i', help='Header image path')
@click.option('--output-dir', '-o', help='Output directory (default: _posts)')
def main(title, tags, image, output_dir):
    """
    Create a new blog post with a template.

    Opens your default editor after creating the post.
    """
    # Parse tags
    tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

    # Create frontmatter
    frontmatter = format_frontmatter(
        title=title,
        date=datetime.now(),
        tags=tag_list,
        image=image
    )

    # Create post
    full_post = create_post_with_frontmatter(POST_TEMPLATE, frontmatter)

    # Determine output path
    if output_dir is None:
        script_dir = Path(__file__).parent.parent
        output_dir = script_dir / "_posts"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    filename = generate_filename(title)
    output_path = output_dir / filename

    # Check if file exists
    if output_path.exists():
        if not click.confirm(f"File {filename} already exists. Overwrite?", default=False):
            click.echo("Cancelled.")
            return

    # Write the file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_post)

    click.echo(f"✓ Post created: {output_path}")

    # Try to open in editor
    editor = click.get_text_stream('stdin').isatty()
    if editor:
        click.edit(filename=str(output_path))


if __name__ == '__main__':
    main()

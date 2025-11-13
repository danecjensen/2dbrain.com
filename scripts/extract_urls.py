#!/usr/bin/env python3
"""
Extract URLs from a text file and format them as references.

Usage:
    python extract_urls.py input.txt
    python extract_urls.py input.txt --fetch-titles --output references.yaml
"""

import sys
import click
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.reference_utils import extract_urls, create_references_from_urls


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file (default: print to console)')
@click.option('--fetch-titles/--no-fetch-titles', default=False,
              help='Fetch page titles for URLs')
@click.option('--format', '-f', type=click.Choice(['yaml', 'markdown', 'text']),
              default='markdown', help='Output format')
def main(input_file, output, fetch_titles, format):
    """
    Extract URLs from a text file and format them as references.

    Examples:

        # Extract URLs and print as Markdown
        python extract_urls.py notes.txt

        # Extract with titles and save as YAML
        python extract_urls.py notes.txt --fetch-titles --format yaml -o refs.yaml

        # Quick extraction without titles
        python extract_urls.py chat.txt --no-fetch-titles
    """
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Extract URLs
    click.echo(f"Extracting URLs from {input_file}...")
    urls = extract_urls(text)

    if not urls:
        click.echo("No URLs found.")
        return

    click.echo(f"Found {len(urls)} unique URL(s)")

    # Create references
    if fetch_titles:
        click.echo("Fetching page titles...")

    references = create_references_from_urls(urls, fetch_titles=fetch_titles)

    # Format output
    if format == 'yaml':
        output_text = yaml.dump(references, default_flow_style=False, allow_unicode=True)
    elif format == 'markdown':
        lines = []
        for i, ref in enumerate(references, 1):
            lines.append(f"{i}. [{ref['title']}]({ref['url']})")
            if 'note' in ref:
                lines.append(f"   *{ref['note']}*")
        output_text = '\n'.join(lines)
    else:  # text
        lines = []
        for i, ref in enumerate(references, 1):
            lines.append(f"{i}. {ref['title']}")
            lines.append(f"   {ref['url']}")
            if 'note' in ref:
                lines.append(f"   Note: {ref['note']}")
            lines.append("")
        output_text = '\n'.join(lines)

    # Output
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(output_text)
        click.echo(f"\n✓ Saved to {output}")
    else:
        click.echo("\n" + "="*60)
        click.echo(output_text)
        click.echo("="*60)


if __name__ == '__main__':
    main()

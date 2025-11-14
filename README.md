# 2dbrain.com - Quick Insights Blog

A Jekyll-based blog system designed for quickly capturing and publishing research insights, with built-in support for citations, YouTube embeds, and automated post creation from LLM conversations.

## Features

- **Markdown-based posts** with rich frontmatter
- **Web-style references** for easy citation management
- **YouTube embed system** with timestamp support
- **Flat tag taxonomy** for easy organization
- **Client-side search** powered by lunr.js
- **Python automation scripts** for common tasks
- **LLM chat converter** supporting ChatGPT, Claude, and Grok

## Quick Start

### Prerequisites

- Ruby 3.1+ and Bundler
- Python 3.9+
- Git

### Installation

1. **Install Ruby dependencies:**
   ```bash
   bundle install
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Jekyll locally:**
   ```bash
   bundle exec jekyll serve
   ```

   Visit `http://localhost:4000` to see your site.

## Creating Posts

### Method 1: Convert LLM Conversation

The easiest way to create a post from your research conversations:

```bash
# Interactive mode (recommended)
python scripts/chat_to_post.py conversation.json

# With options
python scripts/chat_to_post.py chat.json --title "My Insights" --tags ai,productivity

# Fetch page titles for better references
python scripts/chat_to_post.py chat.json --fetch-titles

# Include full conversation
python scripts/chat_to_post.py chat.json --full-conversation
```

**Supported formats:**
- ChatGPT: JSON export from OpenAI
- Claude: Conversation export (JSON or text)
- Grok: JSON or plain text format
- Plain text with "User:" and "Assistant:" markers

### Method 2: Create New Post from Template

```bash
python scripts/new_post.py
```

This will prompt you for:
- Title
- Tags
- Optional header image

### Method 3: Manual Creation

Create a file in `_posts/` with the format `YYYY-MM-DD-title.md`:

```markdown
---
layout: post
title: "Your Post Title"
date: 2024-01-15
tags: [tag1, tag2, tag3]
image: /img/header.png  # optional
references:
  - title: "Reference Title"
    url: "https://example.com"
---

Your content here...
```

## Working with References

### Add Reference to Existing Post

```bash
# Auto-fetch title
python scripts/add_reference.py _posts/2024-01-15-my-post.md https://example.com

# Custom title
python scripts/add_reference.py _posts/my-post.md https://example.com --title "Article Title"

# With note
python scripts/add_reference.py _posts/my-post.md https://example.com --note "Good overview"
```

### Extract URLs from Text

```bash
# Print as Markdown
python scripts/extract_urls.py notes.txt

# Fetch titles and save as YAML
python scripts/extract_urls.py notes.txt --fetch-titles --format yaml -o refs.yaml
```

### Inline Citations

In your Markdown content, reference citations by number:

```markdown
This is a fact that needs citation{% include ref.html id="1" %}.
```

References are automatically numbered and listed at the bottom of the post.

## YouTube Embeds

### Basic Embed

```liquid
{% include youtube.html id="VIDEO_ID" %}
```

### With Timestamp

```liquid
{% include youtube.html id="VIDEO_ID" start="90" %}
```

### With End Time and Caption

```liquid
{% include youtube.html id="VIDEO_ID" start="90" end="120" caption="Key concept explained" %}
```

## Tags and Navigation

### Browse by Tags

Visit `/tags.html` to see all tags and posts organized by topic.

### Search

Visit `/search.html` for full-text search across all posts.

## Conversations Directory

The `conversations/` directory stores interesting AI conversations (ChatGPT, Claude, Grok) that serve as **reference material** for future blog posts.

### Why Use This?

Not every conversation needs to become an immediate post. Save conversations here when:
- You want to preserve research for later
- A topic needs more thought before publishing
- You're gathering material for a comprehensive post
- You want to reference the conversation in future posts

### Saving Conversations

```bash
# Create a new conversation file with metadata
vim conversations/grok-topic-name.md
```

Each file should include:
- **Source**: ChatGPT/Claude/Grok
- **Topic**: Brief description
- **Date Saved**: YYYY-MM-DD
- **Tags**: Relevant tags

See `conversations/README.md` for detailed guidelines.

### Converting to Posts

When ready to publish, use the conversation as source material:

```bash
# Convert directly to a post
python scripts/chat_to_post.py conversations/my-conversation.md

# Extract URLs for references
python scripts/extract_urls.py conversations/my-conversation.md

# Search for topics
grep -r "topic name" conversations/
```

The original conversation stays in `conversations/` (excluded from Jekyll build) while the post goes to `_posts/`.

## File Structure

```
2dbrain.com/
├── _config.yml           # Jekyll configuration
├── _layouts/             # Page layouts
│   ├── default.html      # Base layout
│   └── post.html         # Blog post layout
├── _includes/            # Reusable components
│   ├── youtube.html      # YouTube embed
│   └── ref.html          # Reference citation
├── _posts/               # Blog posts (Markdown)
├── conversations/        # Saved AI conversations (reference material)
├── scripts/              # Python automation tools
│   ├── chat_to_post.py   # Convert LLM chats
│   ├── new_post.py       # Create new post
│   ├── add_reference.py  # Add reference to post
│   ├── extract_urls.py   # Extract URLs from text
│   └── utils/            # Shared utilities
├── css/                  # Stylesheets
├── js/                   # JavaScript
│   └── search.js         # Search functionality
├── img/                  # Images
├── index.html            # Homepage
├── tags.html             # Tag browser
├── search.html           # Search page
└── bio.html              # About page
```

## Python Scripts Reference

### chat_to_post.py

Convert LLM conversations to blog posts.

**Options:**
- `--title, -t`: Post title
- `--tags, -g`: Comma-separated tags
- `--output-dir, -o`: Output directory
- `--fetch-titles`: Fetch page titles for URLs
- `--full-conversation`: Include full chat transcript
- `--no-interactive`: Non-interactive mode

### new_post.py

Create a new post from template.

**Options:**
- `--title, -t`: Post title
- `--tags, -g`: Comma-separated tags
- `--image, -i`: Header image path
- `--output-dir, -o`: Output directory

### add_reference.py

Add a reference to an existing post.

**Usage:**
```bash
python scripts/add_reference.py POST_FILE URL [OPTIONS]
```

**Options:**
- `--title, -t`: Reference title
- `--note, -n`: Optional note
- `--no-fetch`: Don't fetch page title

### extract_urls.py

Extract URLs from a text file.

**Options:**
- `--output, -o`: Output file
- `--fetch-titles`: Fetch page titles
- `--format, -f`: Output format (yaml|markdown|text)

## Deployment

### GitHub Pages

The site is configured to deploy automatically to GitHub Pages via GitHub Actions.

1. Push to the main branch:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. GitHub Actions will automatically build and deploy your site.

### Manual Build

```bash
bundle exec jekyll build
```

The site will be generated in `_site/`.

## Customization

### Styling

- Main stylesheet: `css/verdana-sm.css`
- Post-specific styles: Embedded in `_layouts/post.html`
- Search styles: Embedded in `search.html`

### Configuration

Edit `_config.yml` to customize:
- Site title and description
- Navigation links
- Jekyll plugins
- Permalink structure

## Tips for Quick Insights

1. **Save conversations**: Export ChatGPT/Claude/Grok conversations regularly
2. **Use fetch-titles**: Add `--fetch-titles` when converting to get proper reference titles
3. **Tag consistently**: Use consistent tags across posts for better organization
4. **Extract URLs first**: Use `extract_urls.py` to preview references before creating post
5. **Edit after generation**: The scripts create drafts - always review and enhance

## Workflow Example

Here's a typical workflow for turning research into a blog post:

```bash
# 1. Export your LLM conversation
# (Download as JSON from ChatGPT/Claude/Grok)

# 2. Convert to blog post
python scripts/chat_to_post.py research-chat.json --fetch-titles

# 3. Review and edit the generated post
vim _posts/2024-01-15-my-research-insights.md

# 4. Preview locally
bundle exec jekyll serve

# 5. Commit and push
git add _posts/2024-01-15-my-research-insights.md
git commit -m "Add research insights on X"
git push origin main
```

## Troubleshooting

### Jekyll won't start
- Run `bundle install` to ensure all gems are installed
- Check Ruby version: `ruby --version` (need 3.1+)

### Python scripts fail
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.9+)

### Search not working
- Ensure `search-data.json` is being generated by Jekyll
- Check browser console for errors
- Make sure lunr.js is loading from CDN

### References not showing
- Check frontmatter format in your post
- Ensure `references` is a list of dictionaries with `title` and `url`

## Design Philosophy

Inspired by:
- **Gwern.net**: Rich citation systems and hierarchical content
- **Simon Willison's TIL**: Simplicity and ease of capturing quick learnings

This system prioritizes:
- **Speed**: Quick capture and publication of insights
- **Simplicity**: Markdown files, flat structure, minimal configuration
- **Automation**: Python scripts for repetitive tasks
- **Citability**: Proper references and source attribution

## License

This is a personal blog system. Feel free to use and adapt for your own blog.

## Contributing

This is a personal project, but suggestions are welcome via issues.

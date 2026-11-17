#!/usr/bin/env python3
"""
Markdown Parser for PDF Forge
Extracts structured data from markdown files for template rendering.
"""

import re
from pathlib import Path
from typing import Optional
import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension


def generate_slug(text: str) -> str:
    """
    Generate a URL-safe slug from heading text for use as HTML id attributes.
    Strips non-alphanumeric characters, replaces spaces with hyphens, lowercases.
    """
    slug = text.lower().strip()
    # Remove non-alphanumeric characters (keep spaces and hyphens)
    slug = re.sub(r'[^\w\s-]', '', slug)
    # Replace whitespace with hyphens
    slug = re.sub(r'[\s]+', '-', slug)
    # Collapse multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    # Strip leading/trailing hyphens
    slug = slug.strip('-')
    return slug


def preprocess_markdown(content: str) -> str:
    """
    Preprocess markdown to fix common parsing issues.
    """
    # Ensure blank line before tables (required for many markdown parsers)
    # Match: non-blank line followed by table header row
    content = re.sub(
        r'(\S[^\n]*)\n(\|[^\n]+\|)\n(\|[-:| ]+\|)',
        r'\1\n\n\2\n\3',
        content
    )

    # Normalize multiple blank lines to max 2
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content


def parse_markdown_file(filepath: str) -> dict:
    """
    Parse a markdown file and extract structured content.

    Returns:
        dict with keys:
            - title: Document title (from first H1)
            - subtitle: Optional subtitle
            - date: Extracted date if present
            - executive_summary: Summary section content (HTML)
            - verdict: Dict with type, label, text
            - sections: List of section dicts with title, content, subsections
            - sources: List of source dicts
            - open_questions: List of question strings
            - toc: Table of contents entries
            - raw_html: Full document as HTML
    """
    filepath = Path(filepath).expanduser()
    content = filepath.read_text(encoding='utf-8')

    # Strip YAML frontmatter (the --- delimited block at the top of Zettelkasten files)
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            content = content[end + 3:].lstrip('\n')

    # Preprocess to fix table parsing issues
    content = preprocess_markdown(content)

    result = {
        'title': None,
        'subtitle': None,
        'date': None,
        'executive_summary': None,
        'verdict': None,
        'sections': [],
        'sources': [],
        'open_questions': [],
        'toc': [],
        'raw_html': None,
    }

    # Extract title from first H1
    title_match = re.search(r'^#\s+(.+?)(?:\s*-\s*(.+))?$', content, re.MULTILINE)
    if title_match:
        result['title'] = title_match.group(1).strip()
        if title_match.group(2):
            result['subtitle'] = title_match.group(2).strip()
        # Drop the H1 line from the body content. The cover page renders
        # the title and subtitle separately, so leaving it in place would
        # duplicate it as a heading at the top of the main content.
        content = content[:title_match.start()] + content[title_match.end():]
        content = content.lstrip('\n')

    # Extract date from filename or content
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', str(filepath))
    if date_match:
        result['date'] = date_match.group(1)

    # Parse sections
    sections = parse_sections(content)

    # Find executive summary
    for section in sections:
        if 'executive summary' in section['title'].lower():
            result['executive_summary'] = section['html']
            # Look for verdict in summary
            result['verdict'] = extract_verdict(section['raw'])
        elif 'sources' in section['title'].lower() or 'references' in section['title'].lower():
            result['sources'] = extract_sources(section['raw'])
        elif 'open questions' in section['title'].lower():
            result['open_questions'] = extract_questions(section['raw'])
        else:
            # Regular section
            result['sections'].append({
                'title': section['title'],
                'slug': generate_slug(section['title']),
                'content': section['html'],
                'subsections': section.get('subsections', [])
            })

    # Build TOC
    result['toc'] = build_toc(content)

    # Count H2-level TOC entries for auto-TOC threshold
    result['h2_count'] = sum(1 for entry in result['toc'] if entry['level'] == 1)

    # Convert full document to HTML - NO nl2br
    md = markdown.Markdown(extensions=[
        TableExtension(),
        FencedCodeExtension(),
    ])
    raw_html = md.convert(content)
    raw_html = wrap_tables_for_page_breaks(raw_html)
    result['raw_html'] = add_heading_ids(raw_html)

    return result


def parse_sections(content: str) -> list:
    """
    Split content into sections based on H2 headers.
    """
    sections = []

    # Split by H2 headers
    pattern = r'^##\s+(.+)$'
    parts = re.split(pattern, content, flags=re.MULTILINE)

    # First part is before any H2 (usually title area, skip it)
    i = 1
    while i < len(parts) - 1:
        title = parts[i].strip()
        raw_content = parts[i + 1] if i + 1 < len(parts) else ''

        # Parse subsections (H3)
        subsections = parse_subsections(raw_content)

        # Remove ALL H3 sections from main content using regex
        # This is more robust than string replacement
        main_content = re.sub(
            r'^###\s+.+$.*?(?=^###\s+|\Z)',
            '',
            raw_content,
            flags=re.MULTILINE | re.DOTALL
        )

        # Convert to HTML - NO nl2br as it breaks table rendering
        md = markdown.Markdown(extensions=[
            TableExtension(),
            FencedCodeExtension(),
        ])

        # Convert and wrap tables in divs for better page break control
        html_content = md.convert(main_content.strip())
        html_content = wrap_tables_for_page_breaks(html_content)

        sections.append({
            'title': title,
            'raw': raw_content,
            'html': html_content,
            'subsections': subsections
        })

        i += 2

    return sections


def add_heading_ids(html: str) -> str:
    """
    Add id attributes to h2 and h3 tags in HTML based on their text content.
    Enables clickable TOC anchors to jump to the correct section.
    """
    def replace_heading(match):
        tag = match.group(1)  # h2 or h3
        attrs = match.group(2)  # existing attributes (if any)
        text = match.group(3)  # heading text content
        slug = generate_slug(text)
        # Preserve existing attributes, add id
        if attrs:
            return f'<{tag}{attrs} id="{slug}">{text}</{tag}>'
        return f'<{tag} id="{slug}">{text}</{tag}>'

    # Match h2 and h3 tags, capturing tag name, optional attributes, and content
    html = re.sub(
        r'<(h[23])([^>]*)>([^<]+)</\1>',
        replace_heading,
        html
    )
    return html


def wrap_tables_for_page_breaks(html: str) -> str:
    """
    Wrap <table> elements in divs with page-break-inside:avoid.
    WeasyPrint handles this better on wrapper divs than on tables directly.
    """
    # Simple replacement - wrap each table in a div
    html = re.sub(
        r'(<table[^>]*>)',
        r'<div class="table-wrapper">\1',
        html
    )
    html = re.sub(
        r'(</table>)',
        r'\1</div>',
        html
    )
    return html


def parse_subsections(content: str) -> list:
    """
    Extract H3 subsections from section content.
    """
    subsections = []

    pattern = r'^###\s+(.+)$'
    parts = re.split(pattern, content, flags=re.MULTILINE)

    i = 1
    while i < len(parts) - 1:
        title = parts[i].strip()
        raw_content = parts[i + 1] if i + 1 < len(parts) else ''

        # Preprocess the subsection content for table parsing
        raw_content = preprocess_markdown(raw_content)

        # NO nl2br - breaks table rendering
        md = markdown.Markdown(extensions=[
            TableExtension(),
            FencedCodeExtension(),
        ])

        html_content = md.convert(raw_content.strip())
        html_content = wrap_tables_for_page_breaks(html_content)

        subsections.append({
            'title': title,
            'slug': generate_slug(title),
            'raw': raw_content.strip(),
            'html': html_content
        })

        i += 2

    return subsections


def extract_verdict(content: str) -> Optional[dict]:
    """
    Extract verdict/recommendation from content.
    Looks for patterns like "Act now", "Bookmark", "Ignore"
    """
    # Common verdict patterns
    patterns = [
        (r'act\s*now|take\s*action|do\s*this', 'act', 'Act Now'),
        (r'bookmark|save\s*for\s*later|watch', 'bookmark', 'Bookmark'),
        (r'ignore|skip|pass', 'ignore', 'Ignore'),
    ]

    content_lower = content.lower()

    for pattern, verdict_type, label in patterns:
        if re.search(pattern, content_lower):
            # Try to extract the verdict text
            # Look for bold text or explicit verdict statements
            verdict_match = re.search(
                rf'\*\*({pattern}[^*]*)\*\*|(?:verdict|recommendation)[:\s]*(.+?)(?:\n|$)',
                content,
                re.IGNORECASE
            )
            text = verdict_match.group(1) or verdict_match.group(2) if verdict_match else ''

            return {
                'type': verdict_type,
                'label': label,
                'text': text.strip() if text else f"Recommended action: {label}"
            }

    return None


def extract_sources(content: str) -> list:
    """
    Extract sources/references from content.
    """
    sources = []

    # Look for URLs
    url_pattern = r'(?:\[([^\]]+)\]\(([^)]+)\)|(?:https?://[^\s\)]+))'

    for match in re.finditer(url_pattern, content):
        if match.group(1):  # Markdown link
            sources.append({
                'title': match.group(1),
                'url': match.group(2)
            })
        else:  # Plain URL
            sources.append({
                'title': match.group(0),
                'url': match.group(0)
            })

    # Also look for bullet points without URLs
    bullet_pattern = r'^[-*]\s+(.+)$'
    for match in re.finditer(bullet_pattern, content, re.MULTILINE):
        text = match.group(1).strip()
        # Skip if it's a URL we already captured
        if not any(s.get('title') == text or (s.get('url') and s.get('url') in text) for s in sources):
            if '[' not in text:  # Not a markdown link
                sources.append({'title': text, 'url': None})

    return sources


def extract_questions(content: str) -> list:
    """
    Extract open questions from content.
    """
    questions = []

    # Look for bullet points
    bullet_pattern = r'^[-*]\s+(.+)$'
    for match in re.finditer(bullet_pattern, content, re.MULTILINE):
        questions.append(match.group(1).strip())

    # Also look for numbered items
    numbered_pattern = r'^\d+\.\s+(.+)$'
    for match in re.finditer(numbered_pattern, content, re.MULTILINE):
        questions.append(match.group(1).strip())

    return questions


def build_toc(content: str) -> list:
    """
    Build table of contents from headers.
    """
    toc = []

    # Find all headers H2 and H3
    pattern = r'^(#{2,3})\s+(.+)$'

    for match in re.finditer(pattern, content, re.MULTILINE):
        level = len(match.group(1)) - 1  # H2 = level 1, H3 = level 2
        title = match.group(2).strip()

        # Skip executive summary and sources for TOC
        if any(skip in title.lower() for skip in ['executive summary', 'sources', 'references']):
            continue

        toc.append({
            'level': level,
            'title': title,
            'slug': generate_slug(title),
        })

    return toc


def detect_template(content: str, filepath: str = None) -> str:
    """
    Auto-detect which template to use based on content.
    """
    content_lower = content.lower()

    # Research report indicators
    research_indicators = [
        'executive summary',
        'research swarm',
        'sources',
        'open questions',
        'verdict',
        'findings',
    ]

    research_score = sum(1 for ind in research_indicators if ind in content_lower)

    if research_score >= 2:
        return 'research-report'

    # Check filename
    if filepath:
        filepath_lower = str(filepath).lower()
        if 'research' in filepath_lower:
            return 'research-report'
        if 'guide' in filepath_lower:
            return 'guide'

    # Default to guide for simpler documents
    return 'guide'


if __name__ == '__main__':
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python markdown_parser.py <markdown_file>")
        sys.exit(1)

    result = parse_markdown_file(sys.argv[1])

    # Print summary
    print(f"Title: {result['title']}")
    print(f"Subtitle: {result['subtitle']}")
    print(f"Date: {result['date']}")
    print(f"Sections: {len(result['sections'])}")
    print(f"Sources: {len(result['sources'])}")
    print(f"TOC entries: {len(result['toc'])}")
    print(f"Has executive summary: {result['executive_summary'] is not None}")
    print(f"Has verdict: {result['verdict'] is not None}")

    if '--json' in sys.argv:
        # Remove raw_html for cleaner output
        result_clean = {k: v for k, v in result.items() if k != 'raw_html'}
        print(json.dumps(result_clean, indent=2))

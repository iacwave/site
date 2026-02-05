#!/usr/bin/env python3
"""
Markdown to HTML converter for IACWave posts with SEO and metadata support.

Frontmatter format (optional):
  # Title
  Author: Name
  Tags: tag1, tag2, tag3
  Description: Short description

Markdown features:
  - Headings: # ## ###
  - Lists: - item
  - Bold: **text**
  - Italic: *text*
  - Links: [text](url)
  - Images: ![alt](image.jpg)
  - Blockquotes: > quote
  - Inline code: `code`
"""
import sys
import re
import json
from datetime import date
import argparse


def md_to_html(md_text):
    """Convert markdown to HTML with support for images, bold, italic, blockquotes"""
    html_lines = []
    in_list = False
    in_ol = False
    
    for line in md_text.splitlines():
        line = line.rstrip()
        if not line:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if in_ol:
                html_lines.append('</ol>')
                in_ol = False
            html_lines.append('')
            continue

        # headings
        if line.startswith('### '):
            if in_list: html_lines.append('</ul>'); in_list = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            html_lines.append(f"<h3>{escape_inline(line[4:])}</h3>")
            continue
        if line.startswith('## '):
            if in_list: html_lines.append('</ul>'); in_list = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            html_lines.append(f"<h2>{escape_inline(line[3:])}</h2>")
            continue
        if line.startswith('# '):
            if in_list: html_lines.append('</ul>'); in_list = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            html_lines.append(f"<h1>{escape_inline(line[2:])}</h1>")
            continue

        # blockquote
        if line.startswith('> '):
            if in_list: html_lines.append('</ul>'); in_list = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            html_lines.append(f"<blockquote>{escape_inline(line[2:])}</blockquote>")
            continue

        # numbered list
        if re.match(r'^\d+\.\s', line):
            if in_list: html_lines.append('</ul>'); in_list = False
            if not in_ol: html_lines.append('<ol>'); in_ol = True
            text = re.sub(r'^\d+\.\s', '', line)
            html_lines.append(f"  <li>{escape_inline(text)}</li>")
            continue

        # unordered list
        if line.startswith('- '):
            if in_ol: html_lines.append('</ol>'); in_ol = False
            if not in_list: html_lines.append('<ul>'); in_list = True
            html_lines.append(f"  <li>{escape_inline(line[2:])}</li>")
            continue

        # paragraph with possible images
        if in_list: html_lines.append('</ul>'); in_list = False
        if in_ol: html_lines.append('</ol>'); in_ol = False
        
        # check for image markdown ![alt](src)
        if line.startswith('!['):
            html_lines.append(process_images(line))
        else:
            html_lines.append(f"<p>{escape_inline(line)}</p>")

    if in_list:
        html_lines.append('</ul>')
    if in_ol:
        html_lines.append('</ol>')

    return '\n'.join(l for l in html_lines if l is not None)


def process_images(line):
    """Process markdown images ![alt](src) -> <img src alt>"""
    return re.sub(r"!\[(.*?)\]\((.*?)\)", r"<img src='\2' alt='\1' />", line)


def escape_inline(text):
    """Escape and convert markdown inline elements"""
    # images
    text = re.sub(r"!\[(.*?)\]\((.*?)\)", r"<img src='\2' alt='\1' />", text)
    # links
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"<a href='\2'>\1</a>", text)
    # bold **text**
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    # italic *text*
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
    # inline code `text`
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # simple escaping
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    # restore tags after escaping
    text = text.replace('&lt;strong&gt;', '<strong>').replace('&lt;/strong&gt;', '</strong>')
    text = text.replace('&lt;em&gt;', '<em>').replace('&lt;/em&gt;', '</em>')
    text = text.replace('&lt;code&gt;', '<code>').replace('&lt;/code&gt;', '</code>')
    text = text.replace('&lt;a href=', '<a href=').replace('&lt;/a&gt;', '</a>')
    text = text.replace('&lt;img ', '<img ')
    return text


def estimate_reading_time(text):
    """Estimate reading time in minutes (assuming 200 words per minute)"""
    words = len(text.split())
    minutes = max(1, round(words / 200))
    return minutes


def render_template(template_path, title, description, content_html, date_str, author='IACWave', tags_html='', url='', image='', reading_time=5):
    with open(template_path, 'r', encoding='utf-8') as f:
        tpl = f.read()
    tpl = tpl.replace('{{ title }}', title)
    tpl = tpl.replace('{{ description }}', description)
    tpl = tpl.replace('{{ content }}', content_html)
    tpl = tpl.replace('{{ date }}', date_str)
    tpl = tpl.replace('{{ author }}', author)
    tpl = tpl.replace('{{ tags }}', tags_html)
    tpl = tpl.replace('{{ url }}', url)
    tpl = tpl.replace('{{ image }}', image)
    tpl = tpl.replace('{{ readingTime }}', str(reading_time))
    return tpl


def main():
    parser = argparse.ArgumentParser(description='Convert markdown post to HTML with SEO metadata')
    parser.add_argument('input', help='input markdown file')
    parser.add_argument('output', help='output html file')
    parser.add_argument('--base-url', default='https://iacwave.com.br', help='Site base URL')
    args = parser.parse_args()

    in_md = args.input
    out_html = args.output
    base_url = args.base_url.rstrip('/')

    with open(in_md, 'r', encoding='utf-8') as f:
        md = f.read()

    # Parse frontmatter
    lines = md.splitlines()
    title = 'Post'
    description = ''
    author = 'IACWave'
    tags = []
    start_idx = 0
    
    # Line 1: # Title
    if lines and lines[0].startswith('# '):
        title = lines[0][2:].strip()
        start_idx = 1
    
    # Subsequent lines: Author: name, Tags: tag1, tag2
    while start_idx < len(lines):
        line = lines[start_idx]
        if line.lower().startswith('author:'):
            author = line.split(':', 1)[1].strip()
            start_idx += 1
        elif line.lower().startswith('tags:'):
            tags = [t.strip() for t in line.split(':', 1)[1].split(',')]
            start_idx += 1
        elif line.lower().startswith('description:'):
            description = line.split(':', 1)[1].strip()
            start_idx += 1
        else:
            break

    content_md = '\n'.join(lines[start_idx:]).strip()
    content_html = md_to_html(content_md)
    today = date.today().isoformat()
    
    # Reading time
    reading_time = estimate_reading_time(content_md)

    # Resolve template path
    import os
    script_dir = os.path.dirname(os.path.realpath(__file__))
    tpl_path = os.path.join(script_dir, '..', 'assets', 'templates', 'post_template.html')

    # Build canonical URL and image path
    out_rel = '/' + out_html.replace('../', '').lstrip('/')
    canonical = f"{base_url}{out_rel if out_rel.startswith('/') else '/' + out_rel}"
    image_path = f"{base_url}/logo_iacwave.png"

    # Build tags HTML
    tags_html = ''
    if tags:
        tags_html = '<div style="margin:16px 0">'
        for tag in tags:
            tags_html += f'<span class="tag">{tag.strip()}</span>'
        tags_html += '</div>'

    # JSON-LD with keywords
    jsonld_obj = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "image": image_path,
        "author": {"@type": "Person", "name": author},
        "publisher": {"@type": "Organization", "name": "IACWave", "logo": {"@type": "ImageObject", "url": image_path}},
        "datePublished": today,
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "keywords": ", ".join(tags) if tags else "DevOps, Cloud, IaC"
    }

    jsonld = json.dumps(jsonld_obj, ensure_ascii=False, indent=2)

    html = render_template(tpl_path, title, description, content_html, today, author, tags_html, canonical, image_path, reading_time)
    html = html.replace('{{ jsonld }}', jsonld)

    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'✓ Wrote {out_html} ({reading_time} min read, {len(tags)} tags)')


if __name__ == '__main__':
    main()

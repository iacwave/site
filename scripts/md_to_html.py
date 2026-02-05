#!/usr/bin/env python3
"""
Simple Markdown to HTML converter for IACWave posts.

Usage:
  python3 md_to_html.py posts/input.md ../blog/output-slug.html

This is a lightweight converter (no external deps). It supports headings (#, ##, ###),
unordered lists (- ), paragraphs, and links [text](url).
"""
import sys
import re
import json
from datetime import date
import argparse


def md_to_html(md_text):
    html_lines = []
    in_list = False
    for line in md_text.splitlines():
        line = line.rstrip()
        if not line:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append('')
            continue

        # headings
        if line.startswith('### '):
            html_lines.append(f"<h3>{escape_inline(line[4:])}</h3>")
            continue
        if line.startswith('## '):
            html_lines.append(f"<h2>{escape_inline(line[3:])}</h2>")
            continue
        if line.startswith('# '):
            html_lines.append(f"<h1>{escape_inline(line[2:])}</h1>")
            continue

        # unordered list
        if line.startswith('- '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f"  <li>{escape_inline(line[2:])}</li>")
            continue

        # paragraph
        html_lines.append(f"<p>{escape_inline(line)}</p>")

    if in_list:
        html_lines.append('</ul>')

    return '\n'.join(l for l in html_lines if l is not None)


def escape_inline(text):
    # links [text](url)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"<a href='\2'>\1</a>", text)
    # simple escaping for < and >
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    return text


def render_template(template_path, title, description, content_html, date_str):
    with open(template_path, 'r', encoding='utf-8') as f:
        tpl = f.read()
    tpl = tpl.replace('{{ title }}', title)
    tpl = tpl.replace('{{ description }}', description)
    tpl = tpl.replace('{{ content }}', content_html)
    tpl = tpl.replace('{{ date }}', date_str)
    return tpl


def main():
    parser = argparse.ArgumentParser(description='Convert simple markdown post to HTML using template')
    parser.add_argument('input', help='input markdown file')
    parser.add_argument('output', help='output html file')
    parser.add_argument('--base-url', default='https://iacwave.com.br', help='Site base URL (used for canonical and image links)')
    args = parser.parse_args()

    in_md = args.input
    out_html = args.output
    base_url = args.base_url.rstrip('/')

    with open(in_md, 'r', encoding='utf-8') as f:
        md = f.read()

    # naive front-matter: first line '# Title' and optional 'Description: ...' on second line
    lines = md.splitlines()
    title = 'Post'
    description = ''
    start_idx = 0
    if lines and lines[0].startswith('# '):
        title = lines[0][2:].strip()
        start_idx = 1
    # check for description line
    if len(lines) > start_idx and lines[start_idx].lower().startswith('description:'):
        description = lines[start_idx].split(':', 1)[1].strip()
        start_idx += 1

    content_md = '\n'.join(lines[start_idx:]).strip()
    content_html = md_to_html(content_md)
    today = date.today().isoformat()

    # resolve template path relative to this script
    import os
    script_dir = os.path.dirname(os.path.realpath(__file__))
    tpl_path = os.path.join(script_dir, '..', 'assets', 'templates', 'post_template.html')

    # derive URL and image
    # output path may be like blog/slug.html -> construct canonical
    out_rel = '/' + out_html.replace('../', '').lstrip('/')
    canonical = f"{base_url}{out_rel if out_rel.startswith('/') else '/' + out_rel}"
    # prefer logo_iacwave.png if exists
    image_path = f"{base_url}/logo_iacwave.png"

    jsonld_obj = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "image": image_path,
        "author": {"@type": "Person", "name": "IACWave"},
        "publisher": {"@type": "Organization", "name": "IACWave", "logo": {"@type": "ImageObject", "url": image_path}},
        "datePublished": today,
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical}
    }

    jsonld = json.dumps(jsonld_obj, ensure_ascii=False)

    html = render_template(tpl_path, title, description, content_html, today)
    # replace additional placeholders
    html = html.replace('{{ image }}', image_path)
    html = html.replace('{{ jsonld }}', jsonld)
    html = html.replace('{{ url }}', canonical)

    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'Wrote {out_html}')


if __name__ == '__main__':
    main()

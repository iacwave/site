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
from datetime import date


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
    if len(sys.argv) < 3:
        print('Usage: md_to_html.py input.md output.html')
        sys.exit(2)

    in_md = sys.argv[1]
    out_html = sys.argv[2]

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

    tpl_path = '../assets/templates/post_template.html'
    html = render_template(tpl_path, title, description, content_html, today)

    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'Wrote {out_html}')


if __name__ == '__main__':
    main()

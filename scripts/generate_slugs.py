#!/usr/bin/env python3
"""Generate slug suggestions for papers listed in content.md

Writes images/README-slugs.txt with one slug per paper plus metadata.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(__file__)) if os.path.dirname(__file__) else '.'
MD = os.path.join(ROOT, 'content.md')
OUT_DIR = os.path.join(ROOT, 'images')
OUT_FILE = os.path.join(OUT_DIR, 'README-slugs.txt')

def read_md(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def slugify(text):
    text = text.strip().lower()
    # keep a-z, 0-9 and CJK unified ideographs
    text = re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '-', text)
    text = re.sub(r'-{2,}', '-', text)
    return text.strip('-')

def extract_papers_section(md):
    m = re.search(r'^##\s*部分论文.*$', md, flags=re.M)
    if not m:
        # try English header
        m = re.search(r'^##\s*Papers.*$', md, flags=re.I|re.M)
    if not m:
        return ''
    rest = md[m.end():]
    m2 = re.search(r'^##\s+', rest, flags=re.M)
    return rest[:m2.start()] if m2 else rest

def collect_items(section_md):
    lines = section_md.splitlines()
    items = []
    cur = []
    for line in lines:
        if re.match(r'^\s*\d+\.', line):
            if cur:
                items.append('\n'.join(cur).strip())
                cur = []
            cur.append(re.sub(r'^\s*\d+\.?\s*', '', line))
        else:
            if cur:
                cur.append(line)
    if cur:
        items.append('\n'.join(cur).strip())
    return items

def extract_title(item):
    # look for quoted title (中文书名号或英文引号)
    m = re.search(r'[“\"](.+?)[”\"]', item)
    if m:
        return m.group(1).strip()
    # fallback: text between first pair of quotes-like markers
    # fallback2: up to first comma or period
    m2 = re.split(r'[，,。\.]', item, maxsplit=1)
    return m2[0].strip()

def extract_links(item):
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', item)
    return links

def main():
    if not os.path.exists(MD):
        print('content.md not found at', MD, file=sys.stderr)
        sys.exit(1)
    md = read_md(MD)
    section = extract_papers_section(md)
    items = collect_items(section)
    os.makedirs(OUT_DIR, exist_ok=True)
    lines = []
    for i, item in enumerate(items, 1):
        title = extract_title(item)
        slug = slugify(title) or f'paper-{i}'
        links = extract_links(item)
        lines.append(f'{i}. slug: {slug}')
        lines.append(f'   title: {title}')
        if links:
            for text,url in links:
                lines.append(f'   link: {text} -> {url}')
        lines.append(f'   sample filenames: images/{slug}.jpg  images/{slug}.png  images/{slug}.webp')
        lines.append('')

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print('Wrote', OUT_FILE)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Generate simple SVG placeholder thumbnails for slugs listed in images/README-slugs.txt
Creates images/<slug>.svg when it does not already exist.
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(__file__))
README = os.path.join(ROOT, 'images', 'README-slugs.txt')
OUTDIR = os.path.join(ROOT, 'images')
os.makedirs(OUTDIR, exist_ok=True)

def read_slugs():
    if not os.path.exists(README):
        return []
    out = []
    with open(README, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.match(r'\s*\d+\. slug: (\S+)', line)
            if m:
                out.append(m.group(1).strip())
    return out

SVG_TMPL = '''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200" viewBox="0 0 400 200">
  <rect width="100%" height="100%" fill="#f3f4f6" rx="8"/>
  <text x="16" y="40" font-family="Segoe UI, Roboto, Arial" font-size="16" font-weight="700" fill="#0b1720">{title}</text>
  <text x="16" y="64" font-family="Segoe UI, Roboto, Arial" font-size="12" fill="#374151">Placeholder thumbnail</text>
</svg>'''

def make_svg(slug):
    title = slug.replace('-', ' ')[:48]
    svg = SVG_TMPL.format(title=title)
    path = os.path.join(OUTDIR, f'{slug}.svg')
    if os.path.exists(path):
        return False
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    return True

def main():
    slugs = read_slugs()
    created = 0
    for s in slugs:
        if make_svg(s):
            created += 1
    print('Created', created, 'svg placeholders')

if __name__ == '__main__':
    main()

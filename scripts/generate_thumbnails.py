#!/usr/bin/env python3
"""
一键生成论文缩略图：从 content.md 解析论文，下载 PDF 并渲染第一页为缩略图。

用法:
    python scripts/generate_thumbnails.py

对每篇论文：
  - 若有 PDF 链接（.pdf 或 arxiv） → 下载并渲染第一页为 PNG
  - 若无可用 PDF → 生成 SVG 占位图
所有输出存入 images/<slug>.{png,svg}，已存在的 PNG 自动跳过。
"""

import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_PATH = os.path.join(ROOT, 'content.md')
IMAGES_DIR = os.path.join(ROOT, 'images')

SVG_TMPL = '''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200" viewBox="0 0 400 200">
  <rect width="100%" height="100%" fill="#f3f4f6" rx="8"/>
  <text x="16" y="40" font-family="Segoe UI, Roboto, Arial" font-size="16" font-weight="700" fill="#0b1720">{title}</text>
  <text x="16" y="64" font-family="Segoe UI, Roboto, Arial" font-size="12" fill="#374151">Placeholder thumbnail</text>
</svg>'''


def slugify(text):
    t = text.strip().lower()
    t = re.sub(r'[^a-z0-9一-鿿]+', '-', t)
    t = re.sub(r'-{2,}', '-', t)
    return t.strip('-') or 'paper'


def parse_publications(md):
    """从 content.md 提取论文列表，返回 [{title, slug, links}]"""
    m = re.search(r'^##\s*Publications.*$', md, flags=re.I | re.M)
    if not m:
        return []
    rest = md[m.end():]
    m2 = re.search(r'^##\s+', rest, flags=re.M)
    pubs_text = rest[:m2.start()] if m2 else rest

    # 支持两种列表格式："N. " 序号列表 和 "- " 无序列表（含 "1-" 笔误情况）
    items = re.split(r'\n\s*(?:\d+\.|\d+-|-)\s+', pubs_text)
    result = []
    for item in items[1:]:
        item = item.strip()
        if not item:
            continue
        title_m = re.search(r'[“\"](.+?)[”\"]', item)
        title = title_m.group(1) if title_m else ''
        slug = slugify(title)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', item)
        result.append({'title': title, 'slug': slug, 'links': links})
    return result


def find_pdf_url(links):
    """从链接中找到 PDF 下载地址（优先 .pdf 链接，其次 arxiv）。"""
    for text, url in links:
        u = url.strip()
        if u.lower().endswith('.pdf'):
            return u
        m = re.match(r'https?://arxiv\.org/abs/(.+)$', u)
        if m:
            return f'https://arxiv.org/pdf/{m.group(1)}.pdf'
        m = re.match(r'https?://arxiv\.org/pdf/(.+)$', u)
        if m:
            return u
    return None


def download_pdf(url, timeout=30):
    """下载 PDF 文件，返回 bytes 或 None。"""
    import requests
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        r.raise_for_status()
        ct = r.headers.get('content-type', '')
        if 'application/pdf' not in ct and not url.lower().endswith('.pdf') and len(r.content) < 100_000:
            return None
        return r.content
    except Exception as e:
        print(f'    [warn] {e}')
        return None


def render_pdf_thumbnail(pdf_bytes, out_path, width=200):
    """用 PyMuPDF 渲染 PDF 第一页为 PNG 缩略图。"""
    import fitz
    doc = fitz.open(stream=pdf_bytes, filetype='pdf')
    page = doc.load_page(0)
    vp = page.get_viewport()
    scale = width / vp.width
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    pix.save(out_path)
    doc.close()


def generate_svg_placeholder(slug, title):
    """生成 SVG 占位缩略图。"""
    display = (title or slug.replace('-', ' '))[:48]
    svg = SVG_TMPL.format(title=display)
    path = os.path.join(IMAGES_DIR, f'{slug}.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    return path


def main():
    os.makedirs(IMAGES_DIR, exist_ok=True)

    if not os.path.exists(MD_PATH):
        print('Error: content.md not found')
        sys.exit(1)

    with open(MD_PATH, 'r', encoding='utf-8') as f:
        md = f.read()

    pubs = parse_publications(md)
    print(f'Found {len(pubs)} publications\n')

    stats = {'png': 0, 'svg': 0, 'skip': 0}

    for i, pub in enumerate(pubs, 1):
        label = (pub['title'] or pub['slug'])[:60]
        print(f'[{i}/{len(pubs)}] {label}')

        png_path = os.path.join(IMAGES_DIR, f'{pub["slug"]}.png')
        if os.path.exists(png_path):
            print(f'    [skip] PNG exists')
            stats['skip'] += 1
            continue

        pdf_url = find_pdf_url(pub['links'])
        if pdf_url:
            print(f'    [pdf] {pdf_url}')
            data = download_pdf(pdf_url)
            if data:
                try:
                    render_pdf_thumbnail(data, png_path)
                    print(f'    [ok] PNG: {png_path}')
                    stats['png'] += 1
                    continue
                except Exception as e:
                    print(f'    [warn] Render failed: {e}')

        path = generate_svg_placeholder(pub['slug'], pub['title'])
        print(f'    [svg] {path}')
        stats['svg'] += 1

    print(f'\nDone: {stats["png"]} PNG / {stats["svg"]} SVG / {stats["skip"]} skip')


if __name__ == '__main__':
    main()

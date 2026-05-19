# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

个人学术主页，使用 Markdown 驱动的内容管理系统。编辑 `content.md` 即可更新页面内容，纯静态页面可直接部署到 GitHub Pages。

## 架构

- **index.html** — 单页入口，使用 marked.js 将 Markdown 渲染为 HTML，并用 PDF.js 渲染论文 PDF 第一页作为缩略图（受 CORS 限制，静默失败）
- **content.md** — 所有页面内容（个人信息、论文列表、联系方式），是唯一需要日常维护的文件
- **style.css** — 深蓝色导航栏 + 白色主区域的布局，论文卡片带左侧缩略图
- **scripts/** — Python 辅助脚本（不参与页面运行时渲染）
- **images/** — 论文缩略图和头像，以论文标题的 slug 命名

## 内容维护

编辑 `content.md`，提交并推送后 GitHub Pages 自动发布。

**论文条目格式：** 两种列表格式均支持：
- 有序列表：`序号. 作者, "标题," 期刊/会议, 年份. [[链接文本]](url)`
- 无序列表：`- 作者, "标题," 期刊/会议, 年份. [[链接文本]](url)`

论文列表需放在 `## Publications` 标题下。页面运行时会将列表项渲染为论文卡片（缩略图 + 标题 + 作者 + 元信息 + 链接）。

**头像：** 放在 `images/avatar.jpg`，头像加载失败时自动隐藏。

## 缩略图匹配规则

页面运行时通过论文标题生成 slug，依次尝试以下格式加载图片：
1. `images/<slug>.svg`（优先级最高）
2. `images/<slug>.jpg`
3. `images/<slug>.png`
4. `images/<slug>.webp`
5. 均失败则隐藏该论文的缩略图区域

## 常用命令

```bash
# 生成论文 slug 列表（写入 images/README-slugs.txt）
python scripts/generate_slugs.py

# 为所有论文生成 SVG 占位缩略图
python scripts/generate_svgs.py

# 下载 PDF 并生成第一页作为缩略图（需要安装依赖：pip install requests PyMuPDF）
python scripts/generate_thumbnails.py [--limit N]

# 本地预览
python -m http.server 8000
npx serve .
```

## 工具脚本说明

`generate_slugs.py` 从 `content.md` 的 `## Publications` 标题下提取论文条目，生成 slug 写入 `images/README-slugs.txt`。注意该脚本目前搜索的是 `部分论文` 标题（而非 `Publications`），如有需要需先修改脚本中的正则表达式。

`generate_thumbnails.py` 对每篇论文自动尝试：有 PDF 链接则下载并渲染第一页为 PNG，否则生成 SVG 占位图。已存在的 PNG 自动跳过。

所有脚本的 slug 生成规则：标题转小写，非字母数字和中文替换为连字符，去除首尾连字符。

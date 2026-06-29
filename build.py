#!/usr/bin/env python3
"""
fourthpin — build script
────────────────────────────────────────────────────────────────────
DAILY USE:  edit BREWING or VOCAB below, then run:
              python3 build.py

NEW POST:   drop a .md file in posts/_md/YYYY-MM-DD-slug.md
            with YAML frontmatter, then run:
              python3 build.py
            (rebuilds the post HTML and refreshes blog + home lists)

Setup (one time):
              pip install markdown pyyaml
────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations
import re
from pathlib import Path

# ══════════════════════════════════════════════════════════════════
#  EDIT THESE — then run:  python3 build.py
# ══════════════════════════════════════════════════════════════════

BREWING = {
    "bean":    "Ethiopia Yirgacheffe",
    "roaster": "Onyx Coffee Lab",
    "process": "Natural",
}

VOCAB = {
    "word":  "xin chào",
    "roman": "sin chow",
    "def":   "hello / greetings",
}

# ══════════════════════════════════════════════════════════════════
#  ENGINE — no need to edit below
# ══════════════════════════════════════════════════════════════════

ROOT = Path(__file__).parent


# ── HUD card HTML fragments ───────────────────────────────────────

def _brewing_html() -> str:
    return (
        '  <!-- edit BREWING in build.py → python3 build.py -->\n'
        '  <div class="brewing-card">\n'
        '    <span class="brewing-card-label">now brewing</span>\n'
        f'    <span class="brewing-card-bean">{BREWING["bean"]}</span>\n'
        f'    <span class="brewing-card-roaster">{BREWING["roaster"]}</span>\n'
        f'    <span class="brewing-card-process">{BREWING["process"]}</span>\n'
        '  </div>'
    )


def _vocab_html() -> str:
    return (
        '  <!-- edit VOCAB in build.py → python3 build.py -->\n'
        '  <div class="vocab-card">\n'
        '    <span class="vocab-card-label">từ hôm nay</span>\n'
        f'    <span class="vocab-card-word">{VOCAB["word"]}</span>\n'
        f'    <span class="vocab-card-roman">{VOCAB["roman"]}</span>\n'
        f'    <span class="vocab-card-def">{VOCAB["def"]}</span>\n'
        '  </div>'
    )


# Match any existing card block (comment + div) regardless of prior comment text
_BREWING_RE = re.compile(
    r'  <!--[^\n]*(?:build\.py|switch bags|BREWING)[^\n]*-->\n'
    r'  <div class="brewing-card">.*?</div>',
    re.DOTALL,
)
_VOCAB_RE = re.compile(
    r'  <!--[^\n]*(?:build\.py|new word|VOCAB)[^\n]*-->\n'
    r'  <div class="vocab-card">.*?</div>',
    re.DOTALL,
)


def update_hud_cards() -> None:
    """Propagate BREWING and VOCAB dicts into every HTML file."""
    pages = list(ROOT.glob("*.html")) + list((ROOT / "posts").glob("*.html"))
    pages = [p for p in pages if not p.name.startswith("_")]

    changed = 0
    for path in pages:
        original = path.read_text(encoding="utf-8")
        updated  = _BREWING_RE.sub(_brewing_html(), original)
        updated  = _VOCAB_RE.sub(_vocab_html(), updated)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1

    print(f"  HUD cards → {changed} file(s) updated")


# ── Markdown → post HTML ──────────────────────────────────────────

_POST_LAYOUT = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} \u2014 fourthpin</title>
  <meta name="description" content="{description}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="article">
  <link rel="stylesheet" href="../style.css">
  <link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
</head>
<body>
  <div class="container">

    <header>
      <a href="/" class="site-title">fourthpin</a>
      <nav>
        <a href="../about.html">about</a>
        <a href="../blog.html" aria-current="page">blog</a>
        <a href="../photos.html">photos</a>
      </nav>
    </header>

    <main>

      <a href="../blog.html" class="back-link">all posts</a>

      <article>

        <div class="post-header">
          <h1>{title}</h1>
          <div class="post-meta">
            <span>{date}</span>
{read_time_line}\
{tags_line}\
          </div>
        </div>

        <div class="post-content">
{content}
        </div>

        <nav class="post-nav" aria-label="Post navigation">
{prev_next}\
        </nav>

      </article>
    </main>

    <footer>
      <div class="footer-inner">
        <span>\u00a9 2026 Doug Woodward \u00b7 fourthpin</span>
      </div>
    </footer>

  </div>

{vocab_card}

{brewing_card}
</body>
</html>
"""


def _read_time(text: str) -> str:
    mins = max(1, round(len(text.split()) / 200))
    return f"{mins} MIN READ"


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return {}, text
    try:
        import yaml
        meta = yaml.safe_load(text[3:end]) or {}
    except Exception:
        meta = {}
    return meta, text[end + 4:].lstrip("\n")


def build_posts() -> list[dict]:
    """Convert posts/_md/*.md → posts/*.html with auto prev/next links."""
    posts = _collect_posts()
    if not posts:
        print("  No .md files in posts/_md/ — nothing to build")
        return []

    try:
        import markdown as md_lib
        import yaml  # noqa: F401
    except ImportError:
        print("  Skipping posts — run:  pip install markdown pyyaml")
        return posts

    md_dir = ROOT / "posts" / "_md"
    files = sorted(md_dir.glob("*.md"))
    if not files:
        print("  No .md files in posts/_md/ — nothing to build")
        return []

    # First pass — read all frontmatter so we can wire prev/next
    all_meta: list[dict] = []
    for src in files:
        meta, _ = _parse_frontmatter(src.read_text(encoding="utf-8"))
        meta.setdefault("title", src.stem)
        meta["_src"] = src
        all_meta.append(meta)

    # Second pass — build HTML
    built = 0
    for i, meta in enumerate(all_meta):
        src: Path = meta["_src"]
        _, body = _parse_frontmatter(src.read_text(encoding="utf-8"))

        content_html = md_lib.markdown(
            body,
            extensions=["extra", "smarty"],
            output_format="html",
        )
        indented = "\n".join(
            "          " + ln if ln.strip() else ""
            for ln in content_html.splitlines()
        )

        read_time_line = f"            <span>{_read_time(body)}</span>\n"
        tags           = meta.get("tags", "")
        tags_line      = f'            <span class="tag">{tags}</span>\n' if tags else ""

        # Prev/next (older post = prev, newer = next)
        prev_next = ""
        if i > 0:
            p = all_meta[i - 1]
            href = p["_src"].with_suffix(".html").name
            prev_next += f'          <a href="{href}" class="prev">{p["title"]}</a>\n'
        if i < len(all_meta) - 1:
            n = all_meta[i + 1]
            href = n["_src"].with_suffix(".html").name
            prev_next += f'          <a href="{href}" class="next">{n["title"]}</a>\n'

        html = _POST_LAYOUT.format(
            title          = meta.get("title", src.stem),
            description    = meta.get("description", meta.get("title", src.stem)),
            date           = meta.get("date", ""),
            read_time_line = read_time_line,
            tags_line      = tags_line,
            content        = indented,
            prev_next      = prev_next,
            vocab_card     = _vocab_html(),
            brewing_card   = _brewing_html(),
        )

        out = ROOT / "posts" / src.with_suffix(".html").name
        out.write_text(html, encoding="utf-8")
        built += 1
        print(f"  Built  posts/{src.stem}.html")

    print(f"  {built} post(s) built")
    return _collect_posts()


# ── Post index lists (blog.html + index.html) ─────────────────────

_BLOG_LIST_RE = re.compile(
    r'      <!-- build\.py: post list -->\n'
    r'      <ul class="post-list">.*?</ul>',
    re.DOTALL,
)
_INDEX_LIST_RE = re.compile(
    r'        <!-- build\.py: recent posts -->\n'
    r'        <ul class="post-list">.*?</ul>',
    re.DOTALL,
)


def _post_list_items(posts: list[dict], indent: str, *, href_prefix: str) -> str:
    if not posts:
        return f'{indent}<ul class="post-list">\n{indent}</ul>'
    lines = [f"{indent}<ul class=\"post-list\">"]
    for post in posts:
        lines.append(f"{indent}  <li>")
        lines.append(f'{indent}    <span class="date">{post["date_iso"]}</span>')
        lines.append(
            f'{indent}    <a href="{href_prefix}{post["slug"]}.html">{post["title"]}</a>'
        )
        lines.append(f"{indent}  </li>")
    lines.append(f"{indent}</ul>")
    return "\n".join(lines)


def update_post_lists(posts: list[dict] | None = None) -> None:
    """Refresh blog archive and home recent-post lists from markdown metadata."""
    if posts is None:
        posts = _collect_posts()

    blog_path = ROOT / "blog.html"
    blog_html = blog_path.read_text(encoding="utf-8")
    blog_block = (
        "      <!-- build.py: post list -->\n"
        + _post_list_items(posts, "      ", href_prefix="posts/")
    )
    blog_updated = _BLOG_LIST_RE.sub(blog_block, blog_html)
    if blog_updated != blog_html:
        blog_path.write_text(blog_updated, encoding="utf-8")
        print(f"  blog.html → {len(posts)} post(s)")

    index_path = ROOT / "index.html"
    index_html = index_path.read_text(encoding="utf-8")
    recent = posts[:5]
    index_block = (
        "        <!-- build.py: recent posts -->\n"
        + _post_list_items(recent, "        ", href_prefix="posts/")
    )
    index_updated = _INDEX_LIST_RE.sub(index_block, index_html)
    if index_updated != index_html:
        index_path.write_text(index_updated, encoding="utf-8")
        print(f"  index.html → {len(recent)} recent post(s)")


def _collect_posts() -> list[dict]:
    md_dir = ROOT / "posts" / "_md"
    if not md_dir.is_dir():
        return []

    posts: list[dict] = []
    for src in sorted(md_dir.glob("*.md"), reverse=True):
        meta, _ = _parse_frontmatter(src.read_text(encoding="utf-8"))
        posts.append({
            "slug":     src.stem,
            "date_iso": src.stem[:10],
            "title":    meta.get("title", src.stem),
        })
    return posts


# ── Entry point ───────────────────────────────────────────────────

if __name__ == "__main__":
    print("fourthpin build\n")
    print("› HUD cards")
    update_hud_cards()
    print()
    print("› Posts")
    posts = build_posts()
    print()
    print("› Post lists")
    update_post_lists(posts)
    print("\nDone ✓")

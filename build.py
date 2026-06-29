#!/usr/bin/env python3
"""
fourthpin — build script
────────────────────────────────────────────────────────────────────
DAILY USE:  edit BREWING or VOCAB below, then run:
              python3 build.py
            (logs changes to data/brewing-history.yaml and data/vocab-history.yaml)

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
from datetime import date
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
    "word":  "ván trượt",
    "roman": "vahn truht",
    "def":   "surfboard / skateboard",
}

# ══════════════════════════════════════════════════════════════════
#  ENGINE — no need to edit below
# ══════════════════════════════════════════════════════════════════

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
BREWING_HISTORY_PATH = DATA_DIR / "brewing-history.yaml"
VOCAB_HISTORY_PATH = DATA_DIR / "vocab-history.yaml"


# ── HUD card HTML fragments ───────────────────────────────────────

def _brewing_inner() -> str:
    return (
        '    <div class="brewing-card">\n'
        '      <span class="brewing-card-label">now brewing</span>\n'
        f'      <span class="brewing-card-bean">{BREWING["bean"]}</span>\n'
        f'      <span class="brewing-card-roaster">{BREWING["roaster"]}</span>\n'
        f'      <span class="brewing-card-process">{BREWING["process"]}</span>\n'
        '      <a href="/brewing.html" class="hud-log-link hud-log-link--brewing">Brew Log →</a>\n'
        '    </div>'
    )


def _vocab_inner() -> str:
    return (
        '    <div class="vocab-card">\n'
        '      <span class="vocab-card-label">từ hôm nay</span>\n'
        f'      <span class="vocab-card-word">{VOCAB["word"]}</span>\n'
        f'      <span class="vocab-card-roman">{VOCAB["roman"]}</span>\n'
        f'      <span class="vocab-card-def">{VOCAB["def"]}</span>\n'
        '      <a href="/words.html" class="hud-log-link hud-log-link--vocab">Word Log →</a>\n'
        '    </div>'
    )


def _hud_stack_html() -> str:
    return (
        '  <!-- edit BREWING and VOCAB in build.py → python3 build.py -->\n'
        '  <aside class="hud-stack" aria-label="Status">\n'
        f'{_brewing_inner()}\n'
        f'{_vocab_inner()}\n'
        '  </aside>'
    )


# Legacy single-card matchers (for migrating older HTML)
_BREWING_RE = re.compile(
    r'  <!--[^\n]*(?:build\.py|switch bags|BREWING)[^\n]*-->\n'
    r'  <div class="brewing-card">.*?</div>\n?',
    re.DOTALL,
)
_VOCAB_RE = re.compile(
    r'  <!--[^\n]*(?:build\.py|new word|VOCAB)[^\n]*-->\n'
    r'  <div class="vocab-card">.*?</div>\n?',
    re.DOTALL,
)
_HUD_STACK_RE = re.compile(
    r'  <!--[^\n]*(?:build\.py|BREWING|VOCAB|fourthpin:hud)[^\n]*-->\n'
    r'  <aside class="hud-stack"[^>]*>.*?</aside>\n?',
    re.DOTALL,
)
_HUD_ORPHAN_RE = re.compile(
    r'  <aside class="hud-stack"[^>]*>.*?</aside>\n?',
    re.DOTALL,
)


def _strip_all_hud(html: str) -> str:
    """Remove every HUD stack and legacy card block (may take several passes)."""
    prev = None
    while html != prev:
        prev = html
        html = _HUD_STACK_RE.sub("", html)
        html = _HUD_ORPHAN_RE.sub("", html)
        html = _BREWING_RE.sub("", html)
        html = _VOCAB_RE.sub("", html)
    return re.sub(r"\n{3,}", "\n\n", html)


def update_hud_cards() -> None:
    """Propagate BREWING and VOCAB dicts into every HTML file."""
    pages = list(ROOT.glob("*.html")) + list((ROOT / "posts").glob("*.html"))
    pages = [p for p in pages if not p.name.startswith("_")]

    stack = _hud_stack_html() + "\n"
    changed = 0
    for path in pages:
        original = path.read_text(encoding="utf-8")
        updated = _strip_all_hud(original)
        updated = updated.replace("</body>", f"{stack}</body>", 1)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1

    print(f"  HUD cards → {changed} file(s) updated")

    template = ROOT / "posts" / "_template.html"
    if template.exists():
        original = template.read_text(encoding="utf-8")
        updated = _strip_all_hud(original)
        updated = updated.replace("</body>", f"{stack}</body>", 1)
        if updated != original:
            template.write_text(updated, encoding="utf-8")
            print("  posts/_template.html → HUD updated")


_SKIP_RE = re.compile(r'  <a class="skip-link"[^>]*>Skip to content</a>\n?')


def update_page_accessibility() -> None:
    """Add skip link and main landmark id to static HTML pages."""
    pages = list(ROOT.glob("*.html")) + [ROOT / "posts" / "_template.html"]
    changed = 0
    for path in pages:
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8")
        updated = _SKIP_RE.sub("", original)
        updated = updated.replace("<body>\n", f"<body>\n{_SKIP_LINK}", 1)
        updated = re.sub(r'<main(?![^>]*\bid=)', '<main id="main-content"', updated)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    if changed:
        print(f"  skip links → {changed} file(s) updated")


_FOOTER_LINKS_RE = re.compile(
    r'        <span class="footer-links">.*?</span>\n',
    re.DOTALL,
)
_FOOTER_LINKS = (
    '        <span class="footer-links">\n'
    '          <a href="brewing.html">Brew Log</a>\n'
    '          <a href="words.html">Word Log</a>\n'
    '        </span>\n'
)


def update_footer_links() -> None:
    """Ensure root pages have footer links to log pages."""
    changed = 0
    for path in ROOT.glob("*.html"):
        original = path.read_text(encoding="utf-8")
        updated = _FOOTER_LINKS_RE.sub("", original)
        if _FOOTER_LINKS.strip() not in updated:
            updated = updated.replace(
                "        <span>© 2026 fourthpin</span>\n",
                "        <span>© 2026 fourthpin</span>\n" + _FOOTER_LINKS,
                1,
            )
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    if changed:
        print(f"  footer links → {changed} file(s) updated")


# ── Brewing + vocab history ───────────────────────────────────────

def _load_yaml_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    except Exception:
        return []
    return data if isinstance(data, list) else []


def _save_yaml_list(path: Path, items: list[dict]) -> None:
    import yaml
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.dump(items, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def _matches(entry: dict, current: dict, keys: tuple[str, ...]) -> bool:
    return all(entry.get(k) == current.get(k) for k in keys)


def _sync_history(
    path: Path,
    current: dict,
    keys: tuple[str, ...],
    label: str,
) -> list[dict]:
    """Append to history when values change or a new day starts."""
    history = _load_yaml_list(path)
    today = date.today().isoformat()
    entry = {**current, "date": today}

    if history and _matches(history[0], entry, keys) and history[0].get("date") == today:
        return history

    if not history or not _matches(history[0], entry, keys) or history[0].get("date") != today:
        history.insert(0, entry)
        _save_yaml_list(path, history)
        print(f"  {label} → logged ({len(history)} total)")

    return history


def sync_histories() -> tuple[list[dict], list[dict]]:
    brewing = _sync_history(
        BREWING_HISTORY_PATH,
        BREWING,
        ("bean", "roaster", "process"),
        "brewing history",
    )
    vocab = _sync_history(
        VOCAB_HISTORY_PATH,
        VOCAB,
        ("word", "roman", "def"),
        "vocab history",
    )
    return brewing, vocab


_SKIP_LINK = '  <a class="skip-link" href="#main-content">Skip to content</a>\n'


_PAGE_SHELL = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} \u2014 fourthpin</title>
  <meta name="description" content="{description}">
  <link rel="stylesheet" href="{css_prefix}style.css">
  <link rel="icon" href="{css_prefix}assets/favicon.svg" type="image/svg+xml">
</head>
<body>
{_skip_link}  <div class="container">

    <header>
      <a href="/" class="site-title">fourthpin</a>
      <nav>
        <a href="{css_prefix}about.html">about</a>
        <a href="{css_prefix}blog.html">blog</a>
        <a href="{css_prefix}photos.html">photos</a>
      </nav>
    </header>

    <main id="main-content">
{content}
    </main>

    <footer>
      <div class="footer-inner">
        <span>\u00a9 2026 fourthpin</span>
        <span class="footer-links">
          <a href="{css_prefix}brewing.html">Brew Log</a>
          <a href="{css_prefix}words.html">Word Log</a>
        </span>
      </div>
    </footer>

  </div>

{hud_stack}
</body>
</html>
"""


def _brewing_history_html(history: list[dict]) -> str:
    if not history:
        rows = '      <p class="history-empty">Nothing logged yet.</p>'
    else:
        lines = ['      <ul class="history-list history-list--brewing">']
        for i, entry in enumerate(history):
            is_now = (
                i == 0
                and _matches(entry, BREWING, ("bean", "roaster", "process"))
                and entry.get("date") == date.today().isoformat()
            )
            row_class = ' class="is-current"' if is_now else ""
            lines.append(f'        <li{row_class}>')
            lines.append(f'          <span class="date">{entry.get("date", "")}</span>')
            lines.append('          <div class="history-detail">')
            lines.append(f'            <span class="history-primary">{entry.get("bean", "")}</span>')
            roaster = entry.get("roaster", "")
            process = entry.get("process", "")
            lines.append(f'            <span class="history-secondary">{roaster} \u00b7 {process}</span>')
            lines.append("          </div>")
            lines.append("        </li>")
        lines.append("      </ul>")
        rows = "\n".join(lines)

    content = f"""
      <div class="archive-header">
        <h1>Brew Log</h1>
        <p>Beans on rotation. Newest first. <a href="/words.html">Word log \u2192</a></p>
      </div>
{rows}
"""
    return _PAGE_SHELL.format(
        title="Brew Log",
        description="Coffee brew history on fourthpin.",
        css_prefix="",
        content=content,
        hud_stack=_hud_stack_html(),
        _skip_link=_SKIP_LINK,
    )


def _vocab_history_html(history: list[dict]) -> str:
    if not history:
        rows = '      <p class="history-empty">Nothing logged yet.</p>'
    else:
        lines = ['      <ul class="history-list history-list--vocab">']
        for i, entry in enumerate(history):
            is_now = (
                i == 0
                and _matches(entry, VOCAB, ("word", "roman", "def"))
                and entry.get("date") == date.today().isoformat()
            )
            row_class = ' class="is-current"' if is_now else ""
            lines.append(f'        <li{row_class}>')
            lines.append(f'          <span class="date">{entry.get("date", "")}</span>')
            lines.append('          <div class="history-detail">')
            lines.append(f'            <span class="history-primary history-primary--vocab">{entry.get("word", "")}</span>')
            lines.append(f'            <span class="history-secondary">{entry.get("roman", "")}</span>')
            lines.append(f'            <span class="history-def">{entry.get("def", "")}</span>')
            lines.append("          </div>")
            lines.append("        </li>")
        lines.append("      </ul>")
        rows = "\n".join(lines)

    content = f"""
      <div class="archive-header">
        <h1>Word log</h1>
        <p>Vietnamese words, day by day. Newest first. <a href="/brewing.html">Brew Log \u2192</a></p>
      </div>
{rows}
"""
    return _PAGE_SHELL.format(
        title="Word log",
        description="Vietnamese vocabulary history on fourthpin.",
        css_prefix="",
        content=content,
        hud_stack=_hud_stack_html(),
        _skip_link=_SKIP_LINK,
    )


def build_history_pages(brewing: list[dict], vocab: list[dict]) -> None:
    (ROOT / "brewing.html").write_text(_brewing_history_html(brewing), encoding="utf-8")
    (ROOT / "words.html").write_text(_vocab_history_html(vocab), encoding="utf-8")
    print("  brewing.html + words.html built")


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
  <a class="skip-link" href="#main-content">Skip to content</a>
  <div class="container">

    <header>
      <a href="/" class="site-title">fourthpin</a>
      <nav>
        <a href="../about.html">about</a>
        <a href="../blog.html" aria-current="page">blog</a>
        <a href="../photos.html">photos</a>
      </nav>
    </header>

    <main id="main-content">

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

{post_nav_block}\
      </article>
    </main>

    <footer>
      <div class="footer-inner">
        <span>\u00a9 2026 fourthpin</span>
        <span class="footer-links">
          <a href="../brewing.html">Brew Log</a>
          <a href="../words.html">Word Log</a>
        </span>
      </div>
    </footer>

  </div>

{hud_stack}
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

        post_nav_block = ""
        if prev_next.strip():
            post_nav_block = (
                '        <nav class="post-nav" aria-label="Post navigation">\n'
                f"{prev_next}"
                "        </nav>\n"
            )

        html = _POST_LAYOUT.format(
            title          = meta.get("title", src.stem),
            description    = meta.get("description", meta.get("title", src.stem)),
            date           = meta.get("date", ""),
            read_time_line = read_time_line,
            tags_line      = tags_line,
            content        = indented,
            post_nav_block = post_nav_block,
            hud_stack      = _hud_stack_html(),
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
    print("› History")
    brewing_history, vocab_history = sync_histories()
    build_history_pages(brewing_history, vocab_history)
    print()
    print("› HUD cards")
    update_hud_cards()
    update_page_accessibility()
    update_footer_links()
    print()
    print("› Posts")
    posts = build_posts()
    print()
    print("› Post lists")
    update_post_lists(posts)
    print("\nDone ✓")

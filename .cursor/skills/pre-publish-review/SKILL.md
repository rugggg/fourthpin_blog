---
name: pre-publish-review
description: Run design and SVG critics on fourthpin before deploying to main.
disable-model-invocation: true
---

# Pre-publish review

Run before pushing visual changes to `main` (triggers GitHub Pages deploy).

## Steps

1. List changed files in this session — focus on `*.html`, `style.css`, `assets/*.svg`
2. If HTML or CSS changed → delegate to **design-critic** (read-only)
3. If any SVG changed → delegate to **svg-critic**
4. Run both in parallel when both apply
5. Merge findings into one report:

### Blockers
Must fix before push.

### Suggestions
Optional polish.

### Approved
What's good to ship as-is.

6. Fix blockers, re-run critics if needed, then `python3 build.py` and push

## fourthpin reminders

- `python3 build.py` before commit (HUD cards, posts, history pages)
- Never leave duplicate `.hud-stack` blocks on a page
- Skyline displays at 80px — check SVG at that scale

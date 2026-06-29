# fourthpin — agent context

Static personal site at `blog.fourthpin.com`. No framework, no CSS preprocessor, no client JavaScript.

## Stack

- HTML at repo root + `posts/`
- Single stylesheet: `style.css` (design tokens in `:root`)
- Posts: markdown in `posts/_md/` → `python3 build.py` → HTML
- HUD widgets: `BREWING` / `VOCAB` in `build.py` → propagated site-wide
- Fonts: IBM Plex Serif, Sans, Mono (Google Fonts)
- SVG: `assets/skyline.svg` (footer), `assets/favicon.svg`

## Hard constraints

- Do not add JavaScript unless explicitly requested
- Do not split `style.css` or add a CSS build step
- Keep the liminal / NASA-rust / Hanoi-teal / bone palette
- Deploy via GitHub Actions on push to `main`

## Specialist agents

| Agent | When to use |
|-------|-------------|
| `/design-critic` | After HTML/CSS/layout/typography/a11y changes — read-only review |
| `/svg-critic` | When creating or editing SVG assets — authors and audits line-art |

For visual changes touching both, run both critics in parallel before shipping.

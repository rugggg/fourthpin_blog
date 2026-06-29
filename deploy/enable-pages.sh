#!/bin/bash
# Enable GitHub Pages with optional custom domain (serves at domain root — / links work).
# Usage: ./deploy/enable-pages.sh [yourdomain.com]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOMAIN="${1:-}"

cd "$ROOT"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) required." >&2
  exit 1
fi

REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"

if [[ -n "$DOMAIN" ]]; then
  echo "$DOMAIN" > CNAME
  git add CNAME
  echo "Created CNAME → $DOMAIN"
fi

echo "Enabling GitHub Pages on $REPO (branch: main, path: /) ..."
gh api -X POST "/repos/$REPO/pages" \
  -f build_type=legacy \
  -f source[branch]=main \
  -f source[path]=/ 2>/dev/null || \
gh api -X PUT "/repos/$REPO/pages" \
  -f build_type=legacy \
  -f source[branch]=main \
  -f source[path]=/

if [[ -n "$DOMAIN" ]]; then
  gh api -X PUT "/repos/$REPO/pages" \
    -f cname="$DOMAIN" \
    -f https_enforced=true
  echo ""
  echo "=== DNS for GitHub Pages ==="
  echo ""
  echo "  Apex (@):  A → 185.199.108.153"
  echo "             A → 185.199.109.153"
  echo "             A → 185.199.110.153"
  echo "             A → 185.199.111.153"
  echo "  www:       CNAME → ${REPO%%/*}.github.io"
  echo ""
  echo "Commit and push CNAME + site, then wait a few minutes for HTTPS."
else
  PAGES_URL="https://${REPO%%/*}.github.io/${REPO##*/}/"
  echo ""
  echo "Pages URL (project site — / links need a custom domain):"
  echo "  $PAGES_URL"
  echo ""
  echo "For a proper root URL, re-run with your domain:"
  echo "  ./deploy/enable-pages.sh yourdomain.com"
fi

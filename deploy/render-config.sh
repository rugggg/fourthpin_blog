#!/bin/bash
# Render nginx config from templates.
# Usage: ./deploy/render-config.sh [http|https]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ -f "$SCRIPT_DIR/config.env" ]]; then
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/config.env"
fi

DOMAIN="${DOMAIN:?Set DOMAIN in deploy/config.env or export DOMAIN=yourdomain.com}"
WEB_ROOT="${WEB_ROOT:-/var/www/fourthpin}"
MODE="${1:-http}"

case "$MODE" in
  http)  TEMPLATE="$SCRIPT_DIR/nginx-http.conf.template" ;;
  https) TEMPLATE="$SCRIPT_DIR/nginx-https.conf.template" ;;
  *) echo "Usage: $0 [http|https]" >&2; exit 1 ;;
esac

sed \
  -e "s|__DOMAIN__|$DOMAIN|g" \
  -e "s|__WEB_ROOT__|$WEB_ROOT|g" \
  "$TEMPLATE"

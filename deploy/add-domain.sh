#!/bin/bash
# Local helper — wire your domain into the repo and print DNS records.
# Usage: ./deploy/add-domain.sh fourthpin.com [SERVER_IP]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

DOMAIN="${1:?Usage: ./deploy/add-domain.sh yourdomain.com [SERVER_IP]}"
SERVER_IP="${2:-}"

# Persist for install.sh / render-config.sh on the server
cat > "$SCRIPT_DIR/config.env" <<EOF
DOMAIN=$DOMAIN
DEPLOY_USER=deploy
WEB_ROOT=/var/www/fourthpin
GIT_REPO=/home/deploy/fourthpin.git
EOF

echo "Wrote deploy/config.env (DOMAIN=$DOMAIN)"
echo ""

if [[ -n "$SERVER_IP" ]]; then
  echo "=== DNS records to add at your registrar ==="
  echo ""
  echo "  Type   Name   Value"
  echo "  ─────────────────────────────────────"
  echo "  A      @      $SERVER_IP"
  echo "  A      www    $SERVER_IP"
  echo ""
  echo "  (Some registrars use '@' for the root; others want a blank name.)"
  echo ""
  echo "=== Deploy remote (run on your laptop) ==="
  echo ""
  echo "  git remote add production ssh://deploy@$SERVER_IP/home/deploy/fourthpin.git"
  echo "  python3 build.py && git push production main"
else
  echo "=== DNS records ==="
  echo ""
  echo "  Point @ and www to your VPS public IP, then re-run with the IP:"
  echo "  ./deploy/add-domain.sh $DOMAIN YOUR_SERVER_IP"
  echo ""
  echo "=== GitHub Pages alternative (no VPS) ==="
  echo ""
  echo "  If you prefer free hosting via GitHub Pages + custom domain:"
  echo "  ./deploy/enable-pages.sh $DOMAIN"
fi

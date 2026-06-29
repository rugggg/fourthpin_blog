#!/bin/bash
# Bootstrap a fresh Ubuntu/Debian VPS for fourthpin.
#
# On your laptop — copy this repo to the server, then SSH in and run:
#   cd fourthpin_blog
#   cp deploy/config.env.example deploy/config.env   # edit DOMAIN=
#   sudo bash deploy/install.sh
#
# Or one-liner once config.env exists:
#   sudo DOMAIN=fourthpin.com bash deploy/install.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ -f "$SCRIPT_DIR/config.env" ]]; then
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/config.env"
fi

DOMAIN="${DOMAIN:?Set DOMAIN=fourthpin.com (in deploy/config.env or env)}"
DEPLOY_USER="${DEPLOY_USER:-deploy}"
WEB_ROOT="${WEB_ROOT:-/var/www/fourthpin}"
GIT_REPO="${GIT_REPO:-/home/$DEPLOY_USER/fourthpin.git}"
SITE_NAME="fourthpin"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@$DOMAIN}"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo bash deploy/install.sh" >&2
  exit 1
fi

echo "=== fourthpin server setup ==="
echo "  domain:  $DOMAIN"
echo "  web:     $WEB_ROOT"
echo "  git:     $GIT_REPO"
echo ""

echo "=== 1. Packages ==="
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y nginx certbot python3-certbot-nginx \
  python3 python3-pip git

echo "=== 2. Deploy user ==="
if ! id "$DEPLOY_USER" &>/dev/null; then
  useradd -m -s /bin/bash "$DEPLOY_USER"
  echo "Created user $DEPLOY_USER — add your SSH key to /home/$DEPLOY_USER/.ssh/authorized_keys"
fi

echo "=== 3. Web root ==="
mkdir -p "$WEB_ROOT"
chown -R www-data:www-data "$WEB_ROOT"
chmod -R 755 "$WEB_ROOT"

echo "=== 4. Bare git repo ==="
sudo -u "$DEPLOY_USER" mkdir -p "$(dirname "$GIT_REPO")"
if [[ ! -d "$GIT_REPO" ]]; then
  sudo -u "$DEPLOY_USER" git init --bare "$GIT_REPO"
fi

install -m 0755 "$SCRIPT_DIR/post-receive" "$GIT_REPO/hooks/post-receive"

# Allow deploy user to write web root via hook
usermod -aG www-data "$DEPLOY_USER" 2>/dev/null || true
chown -R "$DEPLOY_USER:www-data" "$WEB_ROOT"
chmod -R g+rwX "$WEB_ROOT"

echo "=== 5. nginx (HTTP — certbot adds TLS next) ==="
"$SCRIPT_DIR/render-config.sh" http > "/etc/nginx/sites-available/$SITE_NAME"
ln -sf "/etc/nginx/sites-available/$SITE_NAME" "/etc/nginx/sites-enabled/$SITE_NAME"
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl enable nginx
systemctl reload nginx

echo "=== 6. TLS with Let's Encrypt ==="
echo "    DNS for $DOMAIN and www.$DOMAIN must point to this server first."
read -r -p "    DNS ready? Run certbot now? [y/N] " REPLY
if [[ "${REPLY,,}" == "y" ]]; then
  certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" \
    --non-interactive --agree-tos -m "$ADMIN_EMAIL" --redirect || {
    echo "    certbot failed — finish DNS, then run:"
    echo "    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
  }
fi

echo ""
echo "=== Server ready ==="
echo ""
echo "1. Add your SSH public key (if not already):"
echo "   ssh-copy-id $DEPLOY_USER@\$(curl -s ifconfig.me)"
echo ""
echo "2. On your laptop, add the production remote and deploy:"
echo "   git remote add production ssh://$DEPLOY_USER@YOUR_SERVER_IP${GIT_REPO}"
echo "   python3 build.py && git push production main"
echo ""
echo "3. If certbot was skipped, after DNS propagates:"
echo "   sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo ""

#!/bin/bash
# VPS setup script for your personal site
# Run these commands on your fresh Ubuntu/Debian VPS
# Replace YOUR_DOMAIN with your actual domain throughout.
#
# This script is intended to be read and run command-by-command,
# not executed all at once — some steps require your input.

set -e

echo "=== 1. Update packages ==="
sudo apt update && sudo apt upgrade -y

echo "=== 2. Install nginx and certbot ==="
sudo apt install -y nginx certbot python3-certbot-nginx

echo "=== 3. Create web root ==="
sudo mkdir -p /var/www/yoursite
sudo chown -R www-data:www-data /var/www/yoursite
sudo chmod -R 755 /var/www/yoursite

echo "=== 4. Create deploy user (optional but recommended) ==="
# sudo useradd -m deploy
# sudo mkdir -p /home/deploy/.ssh
# sudo cp ~/.ssh/authorized_keys /home/deploy/.ssh/
# sudo chown -R deploy:deploy /home/deploy/.ssh

echo "=== 5. Create bare git repo for deploys ==="
# Run as deploy user, or adjust paths as needed:
mkdir -p ~/yoursite.git
git init --bare ~/yoursite.git

echo ""
echo "--- Next: copy deploy/post-receive to ~/yoursite.git/hooks/post-receive"
echo "--- Then: chmod +x ~/yoursite.git/hooks/post-receive"
echo ""

echo "=== 6. Copy nginx config ==="
# Copy deploy/nginx.conf to your server, then:
# sudo cp nginx.conf /etc/nginx/sites-available/yoursite
# sudo ln -s /etc/nginx/sites-available/yoursite /etc/nginx/sites-enabled/
# sudo nginx -t

echo "=== 7. Get TLS certificate ==="
# sudo certbot --nginx -d YOUR_DOMAIN -d www.YOUR_DOMAIN
# Certbot will auto-renew. Verify with: sudo certbot renew --dry-run

echo "=== 8. Reload nginx ==="
# sudo systemctl reload nginx

echo ""
echo "=== Done. Local setup: ==="
echo "  git remote add origin ssh://user@YOUR_SERVER_IP/home/deploy/yoursite.git"
echo "  git push origin main"
echo ""

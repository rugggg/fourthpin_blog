#!/bin/bash
# Deprecated — use install.sh + render-config.sh instead.
# Kept for reference; see deploy/install.sh
exec "$(dirname "$0")/install.sh" "$@"

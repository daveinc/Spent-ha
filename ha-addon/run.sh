#!/usr/bin/env bash
set -e

DATA_DIR="/data"
DB_PATH="${DATA_DIR}/spent.db"
KEY_PATH="${DATA_DIR}/.encryption-key"

export SPENT_DB_PATH="${DB_PATH}"
export SPENT_KEY_PATH="${KEY_PATH}"
export SPENT_DISABLE_CHROMIUM_SANDBOX="true"
export HOSTNAME="127.0.0.1"
export PORT="3000"
export NODE_ENV="production"

# Generate encryption key on first boot so the app can start cleanly
if [ ! -f "${KEY_PATH}" ]; then
    echo "Generating encryption key at ${KEY_PATH}"
    openssl rand -hex 32 > "${KEY_PATH}"
    chmod 600 "${KEY_PATH}"
fi

# Write nginx config with the current ingress path
INGRESS_PATH="${INGRESS_PATH:-}"
if [ -n "${INGRESS_PATH}" ]; then
    sed -i "s|INGRESS_PATH_PLACEHOLDER|${INGRESS_PATH}|g" /etc/nginx/http.d/spent.conf
else
    # No ingress path: use a catch-all location (direct port access)
    sed -i "s|location ~ \^INGRESS_PATH_PLACEHOLDER(/.*)?\\$ {|location / {|g" /etc/nginx/http.d/spent.conf
    sed -i '/INGRESS_PATH_PLACEHOLDER/d' /etc/nginx/http.d/spent.conf
fi

# Start nginx
nginx

echo "Starting Spent Finance on port 3000 (proxied via nginx on 41234)"
exec node /app/server.js

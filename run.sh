#!/usr/bin/env bash
set -e

echo "[spent] Starting Spent Finance addon"

DATA_DIR="/data"
DB_PATH="${DATA_DIR}/spent.db"
KEY_PATH="${DATA_DIR}/.encryption-key"

export SPENT_DB_PATH="${DB_PATH}"
export SPENT_KEY_PATH="${KEY_PATH}"
export SPENT_DISABLE_CHROMIUM_SANDBOX="true"
export HOSTNAME="127.0.0.1"
export PORT="3000"
export NODE_ENV="production"

# Generate encryption key on first boot
if [ ! -f "${KEY_PATH}" ]; then
    echo "[spent] Generating encryption key at ${KEY_PATH}"
    openssl rand -hex 32 > "${KEY_PATH}"
    chmod 600 "${KEY_PATH}"
fi

# Verify the standalone server was built
if [ ! -f "/app/server.js" ]; then
    echo "[spent] ERROR: /app/server.js not found - standalone build missing"
    ls -la /app/ || true
    exit 1
fi

echo "[spent] Starting nginx on port 41234"
nginx

echo "[spent] Starting Next.js on 127.0.0.1:3000"
exec node /app/server.js

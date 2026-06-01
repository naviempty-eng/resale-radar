#!/usr/bin/env bash
set -euo pipefail

if [ -z "${BOT_TOKEN:-}" ]; then
  echo "BOT_TOKEN is required"
  exit 1
fi

if [ -z "${BACKEND_URL:-}" ]; then
  echo "BACKEND_URL is required, for example https://resale-radar-api.onrender.com"
  exit 1
fi

if [ -z "${TELEGRAM_WEBHOOK_SECRET:-}" ]; then
  echo "TELEGRAM_WEBHOOK_SECRET is required"
  exit 1
fi

ENCODED_SECRET="$(python3 - <<'PY'
import os
from urllib.parse import quote

print(quote(os.environ["TELEGRAM_WEBHOOK_SECRET"], safe=""))
PY
)"
WEBHOOK_URL="${BACKEND_URL%/}/api/telegram/webhook/${ENCODED_SECRET}"

curl -sS "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook" >/dev/null
echo
curl -sS -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"${WEBHOOK_URL}\",\"drop_pending_updates\":true}"
echo

#!/usr/bin/env bash
set -euo pipefail

if [ -z "${BOT_TOKEN:-}" ]; then
  echo "BOT_TOKEN is required"
  exit 1
fi

curl -sS "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo"
echo

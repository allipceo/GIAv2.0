#!/usr/bin/env sh
set -eu

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-10}"

term_handler() {
  echo "[start.sh] SIGTERM received. Draining for ${TIMEOUT_SECONDS}s..."
  sleep "${TIMEOUT_SECONDS}"
  echo "[start.sh] Exit."
  exit 0
}

trap term_handler TERM INT

echo "[start.sh] Starting server on ${HOST}:${PORT} (sha=${GIT_SHA:-dev}, ver=${APP_VERSION:-0.0.1})"
exec python -u webhook_server.py



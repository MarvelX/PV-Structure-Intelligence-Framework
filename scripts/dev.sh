#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cleanup() {
  if [[ -n "${API_PID:-}" ]] && kill -0 "${API_PID}" 2>/dev/null; then
    kill "${API_PID}" 2>/dev/null || true
  fi
  if [[ -n "${WEB_PID:-}" ]] && kill -0 "${WEB_PID}" 2>/dev/null; then
    kill "${WEB_PID}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

echo "Starting API on http://127.0.0.1:8000"
(
  cd "${ROOT_DIR}"
  uv run --project apps/api uvicorn api.main:app --app-dir apps/api/src --reload --host 127.0.0.1 --port 8000
) &
API_PID=$!

echo "Starting Web on http://127.0.0.1:5173"
(
  cd "${ROOT_DIR}"
  npm --prefix apps/web run dev -- --host 127.0.0.1 --port 5173
) &
WEB_PID=$!

while true; do
  if ! kill -0 "${API_PID}" 2>/dev/null; then
    wait "${API_PID}"
    exit $?
  fi
  if ! kill -0 "${WEB_PID}" 2>/dev/null; then
    wait "${WEB_PID}"
    exit $?
  fi
  sleep 1
done

#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Installing web dependencies"
(
  cd "${ROOT_DIR}/apps/web"
  npm install
)

echo "Syncing api dependencies"
(
  cd "${ROOT_DIR}/apps/api"
  uv sync
)

echo "Applying api migrations"
(
  cd "${ROOT_DIR}/apps/api"
  uv run python -m api.migrations
)

echo "Preparing runtime directories"
mkdir -p "${ROOT_DIR}/data/runtime/exports"

echo "Setup complete"

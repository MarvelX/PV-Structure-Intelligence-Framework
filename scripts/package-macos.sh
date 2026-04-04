#!/usr/bin/env zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WEB_DIR="${ROOT_DIR}/apps/web"
API_DIR="${ROOT_DIR}/apps/api"
DIST_DIR="${ROOT_DIR}/dist/macos"
APP_NAME="PV Structure Intelligence Framework"
APP_BUNDLE="${DIST_DIR}/${APP_NAME}.app"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "package:macos must run on macOS" >&2
  exit 1
fi

rm -rf "${DIST_DIR}"
mkdir -p "${DIST_DIR}"

echo "Building web frontend"
(
  cd "${WEB_DIR}"
  npm run build
)

echo "Packaging macOS app"
(
  cd "${API_DIR}"
  uv run pyinstaller \
    --noconfirm \
    --clean \
    --windowed \
    --name "${APP_NAME}" \
    --distpath "${DIST_DIR}" \
    --workpath "${DIST_DIR}/build" \
    --specpath "${DIST_DIR}/spec" \
    --paths "${API_DIR}/src" \
    --add-data "${API_DIR}/alembic:alembic" \
    --add-data "${API_DIR}/alembic.ini:." \
    --add-data "${WEB_DIR}/dist:web_dist" \
    --add-data "${ROOT_DIR}/data/assets:data/assets" \
    src/api/launcher.py
)

test -d "${APP_BUNDLE}"
xattr -cr "${APP_BUNDLE}"
codesign --remove-signature "${APP_BUNDLE}" 2>/dev/null || true
codesign -s - --force --deep "${APP_BUNDLE}"
codesign --verify --deep --strict --verbose=2 "${APP_BUNDLE}"
echo "Created ${APP_BUNDLE}"

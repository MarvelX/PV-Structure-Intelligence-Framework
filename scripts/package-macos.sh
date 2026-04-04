#!/usr/bin/env zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WEB_DIR="${ROOT_DIR}/apps/web"
API_DIR="${ROOT_DIR}/apps/api"
DIST_DIR="${ROOT_DIR}/dist/macos"
BUILD_DIR="${DIST_DIR}/build"
SPEC_DIR="${DIST_DIR}/spec"
PYINSTALLER_DIST_DIR="../../dist/macos"
PYINSTALLER_WORK_DIR="../../dist/macos/build"
PYINSTALLER_SPEC_DIR="../../dist/macos/spec"
APP_NAME="PV Structure Intelligence Framework"
APP_BUNDLE="${DIST_DIR}/${APP_NAME}.app"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "package:macos must run on macOS" >&2
  exit 1
fi

rm -rf "${DIST_DIR}"
# PyInstaller does not reliably create the nested work dir when the app name contains spaces.
mkdir -p "${DIST_DIR}" "${BUILD_DIR}/${APP_NAME}" "${SPEC_DIR}"

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
    --distpath "${PYINSTALLER_DIST_DIR}" \
    --workpath "${PYINSTALLER_WORK_DIR}" \
    --specpath "${PYINSTALLER_SPEC_DIR}" \
    --paths "${API_DIR}/src" \
    --add-data "${API_DIR}/alembic:alembic" \
    --add-data "${API_DIR}/alembic.ini:." \
    --add-data "${WEB_DIR}/dist:web_dist" \
    --add-data "${ROOT_DIR}/data/assets:data/assets" \
    src/api/launcher.py
)

test -d "${APP_BUNDLE}"
sleep 2
APP_BUNDLE="${APP_BUNDLE}" zsh -lc '
signed_bundle=0
for attempt in 1 2 3; do
  xattr -cr "$APP_BUNDLE"
  codesign --remove-signature "$APP_BUNDLE" 2>/dev/null || true
  if codesign -s - --force --deep "$APP_BUNDLE" >/dev/null 2>&1 && \
    codesign --verify --deep --strict --verbose=2 "$APP_BUNDLE" >/dev/null 2>&1; then
    signed_bundle=1
    break
  fi
  sleep 1
done

if [[ "$signed_bundle" -ne 1 ]]; then
  xattr -cr "$APP_BUNDLE"
  codesign --remove-signature "$APP_BUNDLE" 2>/dev/null || true
  codesign -s - --force --deep "$APP_BUNDLE"
  codesign --verify --deep --strict --verbose=2 "$APP_BUNDLE"
fi
'
echo "Created ${APP_BUNDLE}"

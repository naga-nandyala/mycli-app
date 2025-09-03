#!/usr/bin/env bash
set -euo pipefail

# Build standalone mycli binary for macOS (current architecture)
# Optional: export MYCLI_WITH_AZURE=1 to bundle azure auth libs

if ! command -v pyinstaller >/dev/null; then
  python -m pip install --upgrade pyinstaller
fi

ARCH=$(uname -m)
VERSION=$(grep '__version__' src/mycli_app/__init__.py | cut -d '"' -f2)

pyinstaller mycli.spec --clean

OUT_DIR=dist
BIN_PATH="${OUT_DIR}/mycli"
if [[ ! -f "$BIN_PATH" ]]; then
  echo "Binary not found at $BIN_PATH" >&2
  exit 1
fi

PKG_NAME="mycli-${VERSION}-macos-${ARCH}"
cp "$BIN_PATH" "mycli"
chmod +x mycli

tar -czf "${PKG_NAME}.tar.gz" mycli
shasum -a 256 "${PKG_NAME}.tar.gz" > "${PKG_NAME}.tar.gz.sha256"

echo "Built ${PKG_NAME}.tar.gz"
cat "${PKG_NAME}.tar.gz.sha256"

#!/usr/bin/env bash
# Equivalente Linux de descargar_assets.ps1 (ver ese archivo para el motivo).
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
V=5.3.3
BASE="https://cdn.jsdelivr.net/npm/bootstrap@${V}/dist"
mkdir -p "$RAIZ/static/css/vendor" "$RAIZ/static/js/vendor"
curl -fsSL "$BASE/css/bootstrap.min.css"      -o "$RAIZ/static/css/vendor/bootstrap.min.css"
curl -fsSL "$BASE/js/bootstrap.bundle.min.js" -o "$RAIZ/static/js/vendor/bootstrap.bundle.min.js"
sha256sum "$RAIZ/static/css/vendor/bootstrap.min.css" "$RAIZ/static/js/vendor/bootstrap.bundle.min.js"

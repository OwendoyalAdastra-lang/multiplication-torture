#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

if [[ ! -d node_modules/electron ]]; then
  echo "Installing dependencies (first run only)..."
  npm install
fi

exec npx electron . --no-sandbox --disable-gpu "$@"
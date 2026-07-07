#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="${SCRIPT_DIR}/dist/GrahamsMultiplicationBlast"
GAME="${SCRIPT_DIR}/graham_multiplication_game.py"

if [[ -x "$APP" ]]; then
    exec "$APP"
fi

exec python3 "$GAME"
#!/usr/bin/env bash
# Launch immediately in fullscreen (skips 10-minute wait) for testing
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"
if [[ ! -d node_modules/electron ]]; then npm install; fi
exec npx electron . --no-sandbox --disable-gpu --disable-gpu-compositing --now "$@"
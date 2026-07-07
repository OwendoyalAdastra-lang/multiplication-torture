#!/usr/bin/env bash
set -euo pipefail

AUTOSTART_FILE="${HOME}/.config/autostart/graham-multiplication-blast.desktop"

if [[ -f "${AUTOSTART_FILE}" ]]; then
  rm -f "${AUTOSTART_FILE}"
  echo "Removed autostart: ${AUTOSTART_FILE}"
else
  echo "No autostart entry found."
fi

echo "The app launcher is still available in the applications menu if you want to open it manually."
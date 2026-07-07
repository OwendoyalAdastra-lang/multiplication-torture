#!/usr/bin/env bash
set -euo pipefail

AUTOSTART_FILE="${HOME}/.config/autostart/multiplication-torture.desktop"
OLD_AUTOSTART="${HOME}/.config/autostart/graham-multiplication-blast.desktop"

for file in "${AUTOSTART_FILE}" "${OLD_AUTOSTART}"; do
  if [[ -f "${file}" ]]; then
    rm -f "${file}"
    echo "Removed autostart: ${file}"
  fi
done

echo "The app launcher is still available in the applications menu if you want to open it manually."
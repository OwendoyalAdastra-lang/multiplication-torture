#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="${SCRIPT_DIR}/dist/GrahamsMultiplicationBlast"
ICON="${SCRIPT_DIR}/graham_math_icon.png"
AUTOSTART_DIR="${HOME}/.config/autostart"
APPS_DIR="${HOME}/.local/share/applications"
AUTOSTART_FILE="${AUTOSTART_DIR}/graham-multiplication-blast.desktop"
LAUNCHER_FILE="${APPS_DIR}/GrahamsMultiplicationBlast.desktop"

if [[ ! -x "${APP}" ]]; then
  echo "App not found at ${APP}"
  echo "Build it first:"
  echo "  python3 ${SCRIPT_DIR}/build_graham_math_app.py"
  exit 1
fi

mkdir -p "${AUTOSTART_DIR}" "${APPS_DIR}"

cat > "${AUTOSTART_FILE}" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Graham's Math Lock
Comment=Starts Graham's multiplication lock screen at login
Exec=/bin/bash -c 'sleep 3 && exec ${APP}'
Icon=${ICON}
Terminal=false
Categories=Education;
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=0
StartupNotify=false
EOF

cat > "${LAUNCHER_FILE}" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Graham's Multiplication Blast
Comment=Practice Graham's whiteboard multiplication facts
Exec=${APP}
Icon=${ICON}
Terminal=false
Categories=Game;Education;
EOF

chmod +x "${APP}"

echo "Installed startup app:"
echo "  ${AUTOSTART_FILE}"
echo "  ${LAUNCHER_FILE}"
echo
echo "Graham's math lock runs hidden at login."
echo "After 10 free minutes, math fullscreen locks in."
echo "He must answer 10 questions correctly to escape."
echo "Parent override: Ctrl+Shift+P, PIN is in graham_multiplication_game.py (PARENT_PIN)."
echo
echo "To remove autostart later, run:"
echo "  ${SCRIPT_DIR}/uninstall_graham_startup.sh"
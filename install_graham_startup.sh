#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER="${SCRIPT_DIR}/launch-torture.sh"
ICON="${SCRIPT_DIR}/graham_math_icon.png"
AUTOSTART_DIR="${HOME}/.config/autostart"
APPS_DIR="${HOME}/.local/share/applications"
AUTOSTART_FILE="${AUTOSTART_DIR}/multiplication-torture.desktop"
LAUNCHER_FILE="${APPS_DIR}/MultiplicationTorture.desktop"

if [[ ! -x "${LAUNCHER}" ]]; then
  chmod +x "${LAUNCHER}"
fi

if [[ ! -d "${SCRIPT_DIR}/node_modules/electron" ]]; then
  echo "Installing Electron (first time setup)..."
  (cd "${SCRIPT_DIR}" && npm install)
fi

mkdir -p "${AUTOSTART_DIR}" "${APPS_DIR}"

cat > "${AUTOSTART_FILE}" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Multiplication Torture
Comment=Starts Multiplication Torture at login
Exec=/bin/bash -c 'sleep 3 && exec ${LAUNCHER}'
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
Name=Multiplication Torture
Comment=A way to force your kids to memorize multiplication facts
Exec=${LAUNCHER}
Icon=${ICON}
Terminal=false
Categories=Game;Education;
EOF

echo "Installed startup app:"
echo "  ${AUTOSTART_FILE}"
echo "  ${LAUNCHER_FILE}"
echo
echo "Multiplication Torture (Electron — no Python) runs hidden at login."
echo "After 10 free minutes, fullscreen torture begins."
echo "10 correct answers required to escape."
echo "Parent override: Ctrl+Shift+P, PIN is in app/app.js (PARENT_PIN)."
echo
echo "To remove autostart later, run:"
echo "  ${SCRIPT_DIR}/uninstall_graham_startup.sh"
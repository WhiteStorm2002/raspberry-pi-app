#!/bin/bash
###############################################################################
# Direktes Start-Skript für die Raspberry Pi App
# Kann verwendet werden wenn der Service nicht funktioniert
###############################################################################

APP_DIR="/opt/raspi-app"
VENV_DIR="${APP_DIR}/venv"

# Prüfe ob Installation existiert
if [ ! -d "${APP_DIR}" ]; then
    echo "❌ App ist nicht installiert!"
    echo "Bitte führe zuerst aus: sudo ./install.sh"
    exit 1
fi

# Prüfe ob Virtual Environment existiert
if [ ! -d "${VENV_DIR}" ]; then
    echo "❌ Virtual Environment nicht gefunden!"
    echo "Bitte führe zuerst aus: sudo ./install.sh"
    exit 1
fi

# Setze DISPLAY für GUI
export DISPLAY=:0
export PYTHONPATH="${APP_DIR}"

echo "🚀 Starte Raspberry Pi Eingangsbereich Display..."
echo "   App-Verzeichnis: ${APP_DIR}"
echo "   Python: ${VENV_DIR}/bin/python3"
echo ""
echo "💡 Drücke STRG+C zum Beenden"
echo ""

# Starte die App
cd "${APP_DIR}"
"${VENV_DIR}/bin/python3" -m app.main


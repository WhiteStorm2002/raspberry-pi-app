#!/bin/bash
###############################################################################
# Entwickler-Update (noch einfacher)
# Kopiert nur die wichtigsten Dateien und startet die App direkt
###############################################################################

APP_DIR="/opt/raspi-app"

# Farben
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔄 Kopiere Dateien...${NC}"

# Kopiere alle Python-Dateien
sudo cp -r src/app/* "${APP_DIR}/app/" 2>/dev/null

echo -e "${GREEN}✅ Dateien aktualisiert${NC}"
echo ""
echo "Starte App zum Testen..."
echo ""

# Starte App direkt
cd "${APP_DIR}"
./venv/bin/python3 -m app.main


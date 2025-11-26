#!/bin/bash
###############################################################################
# Autostart-Setup für Raspberry Pi Eingangsbereich Display
# Dieses Skript richtet den automatischen Start beim Booten ein
###############################################################################

set -e

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[FEHLER]${NC} $1"
}

APP_NAME="raspi-app"
SERVICE_NAME="${APP_NAME}.service"

echo "=========================================="
echo "  Autostart-Setup"
echo "=========================================="
echo ""

# Prüfe ob Service existiert
if ! systemctl list-unit-files | grep -q "${SERVICE_NAME}"; then
    print_error "Service ${SERVICE_NAME} nicht gefunden!"
    echo "Bitte führen Sie zuerst ./install.sh aus."
    exit 1
fi

# Aktiviere Service
print_info "Aktiviere Autostart..."
sudo systemctl enable "${SERVICE_NAME}"

print_success "Autostart aktiviert!"
echo ""
echo "Der Service wird nun bei jedem Systemstart automatisch gestartet."
echo ""
echo "Nützliche Befehle:"
echo "  Autostart deaktivieren: sudo systemctl disable ${SERVICE_NAME}"
echo "  Service starten:        sudo systemctl start ${SERVICE_NAME}"
echo "  Service Status:         sudo systemctl status ${SERVICE_NAME}"
echo ""


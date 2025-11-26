#!/bin/bash
###############################################################################
# Quick-Update für Entwicklung
# Kopiert alle Dateien nach /opt/raspi-app ohne komplettes Update
###############################################################################

# Farben
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNUNG]${NC} $1"
}

print_error() {
    echo -e "${RED}[FEHLER]${NC} $1"
}

# Prüfe Root
if [ "$EUID" -ne 0 ]; then
    print_error "Dieses Skript muss als root ausgeführt werden!"
    echo "Bitte verwenden Sie: sudo $0"
    exit 1
fi

APP_DIR="/opt/raspi-app"
SERVICE_NAME="raspi-app.service"

# Prüfe ob App installiert ist
if [ ! -d "${APP_DIR}" ]; then
    print_error "App ist nicht installiert!"
    echo "Bitte führe zuerst aus: sudo ./install.sh"
    exit 1
fi

echo "=========================================="
echo "  Quick-Update"
echo "=========================================="
echo ""

# Stoppe Service falls läuft
if systemctl is-active --quiet "${SERVICE_NAME}"; then
    print_info "Stoppe Service..."
    systemctl stop "${SERVICE_NAME}"
    SERVICE_WAS_RUNNING=true
else
    SERVICE_WAS_RUNNING=false
fi

# Kopiere alle Python-Dateien
print_info "Kopiere Python-Dateien..."
if [ -d "src/app" ]; then
    cp -r src/app/* "${APP_DIR}/app/"
    print_success "Python-Dateien aktualisiert"
else
    print_error "src/app/ Verzeichnis nicht gefunden!"
    exit 1
fi

# Kopiere requirements.txt
if [ -f "requirements.txt" ]; then
    cp requirements.txt "${APP_DIR}/"
    print_info "requirements.txt aktualisiert"
fi

# Aktualisiere Dependencies (optional)
read -p "Python-Pakete auch aktualisieren? (j/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]; then
    print_info "Aktualisiere Python-Pakete..."
    "${APP_DIR}/venv/bin/pip" install -r "${APP_DIR}/requirements.txt" --upgrade
    print_success "Pakete aktualisiert"
fi

# Starte Service wieder falls er lief
if [ "$SERVICE_WAS_RUNNING" = true ]; then
    print_info "Starte Service wieder..."
    systemctl start "${SERVICE_NAME}"
    print_success "Service gestartet"
fi

echo ""
echo "=========================================="
print_success "Quick-Update abgeschlossen!"
echo "=========================================="
echo ""
echo "Aktualisierte Dateien:"
echo "  - Alle Python-Dateien in src/app/"
echo "  - requirements.txt"
echo ""
echo "Zum Testen:"
echo "  ./run.sh"
echo ""


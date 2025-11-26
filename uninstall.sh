#!/bin/bash
###############################################################################
# Deinstaller für Raspberry Pi App
# Dieses Skript entfernt die Python-Anwendung vom Raspberry Pi
###############################################################################

set -e  # Bei Fehler abbrechen

# Farben für Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Konfiguration
APP_NAME="raspi-app"
APP_DIR="/opt/${APP_NAME}"
CONFIG_DIR="/etc/${APP_NAME}"
LOG_FILE="/var/log/${APP_NAME}.log"
SERVICE_NAME="${APP_NAME}.service"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}"

# Funktionen
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

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Dieses Skript muss als root ausgeführt werden!"
        echo "Bitte verwenden Sie: sudo $0"
        exit 1
    fi
}

confirm_uninstall() {
    echo ""
    print_warning "ACHTUNG: Dies wird die Raspberry Pi App vollständig entfernen!"
    echo ""
    echo "Folgende Komponenten werden gelöscht:"
    echo "  - Anwendung: ${APP_DIR}"
    echo "  - Konfiguration: ${CONFIG_DIR}"
    echo "  - Service: ${SERVICE_FILE}"
    echo "  - Log-Datei: ${LOG_FILE}"
    echo ""
    
    read -p "Möchten Sie wirklich deinstallieren? (j/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Jj]$ ]]; then
        print_info "Deinstallation abgebrochen."
        exit 0
    fi
}

stop_service() {
    print_info "Stoppe Service..."
    
    if systemctl is-active --quiet "${SERVICE_NAME}"; then
        systemctl stop "${SERVICE_NAME}"
        print_success "Service gestoppt"
    else
        print_info "Service läuft nicht"
    fi
}

disable_service() {
    print_info "Deaktiviere Service..."
    
    if systemctl is-enabled --quiet "${SERVICE_NAME}" 2>/dev/null; then
        systemctl disable "${SERVICE_NAME}"
        print_success "Service deaktiviert"
    else
        print_info "Service ist nicht aktiviert"
    fi
}

remove_service() {
    print_info "Entferne Service-Datei..."
    
    if [ -f "${SERVICE_FILE}" ]; then
        rm -f "${SERVICE_FILE}"
        systemctl daemon-reload
        print_success "Service-Datei entfernt"
    else
        print_info "Service-Datei existiert nicht"
    fi
}

remove_app() {
    print_info "Entferne Anwendung..."
    
    if [ -d "${APP_DIR}" ]; then
        rm -rf "${APP_DIR}"
        print_success "Anwendung entfernt"
    else
        print_info "Anwendungsverzeichnis existiert nicht"
    fi
}

remove_config() {
    print_info "Entferne Konfiguration..."
    
    read -p "Konfiguration auch löschen? (j/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        if [ -d "${CONFIG_DIR}" ]; then
            rm -rf "${CONFIG_DIR}"
            print_success "Konfiguration entfernt"
        else
            print_info "Konfigurationsverzeichnis existiert nicht"
        fi
    else
        print_info "Konfiguration wurde behalten"
    fi
}

remove_logs() {
    print_info "Entferne Log-Dateien..."
    
    read -p "Log-Dateien auch löschen? (j/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        if [ -f "${LOG_FILE}" ]; then
            rm -f "${LOG_FILE}"
            print_success "Log-Dateien entfernt"
        else
            print_info "Log-Datei existiert nicht"
        fi
    else
        print_info "Log-Dateien wurden behalten"
    fi
}

cleanup() {
    print_info "Führe Cleanup durch..."
    
    # Systemd Cache leeren
    systemctl reset-failed 2>/dev/null || true
    
    print_success "Cleanup abgeschlossen"
}

# Hauptprogramm
main() {
    echo "=========================================="
    echo "  Raspberry Pi App - Deinstaller"
    echo "=========================================="
    
    check_root
    confirm_uninstall
    
    echo ""
    print_info "Starte Deinstallation..."
    echo ""
    
    stop_service
    disable_service
    remove_service
    remove_app
    remove_config
    remove_logs
    cleanup
    
    echo ""
    echo "=========================================="
    print_success "Deinstallation erfolgreich abgeschlossen!"
    echo "=========================================="
    echo ""
    print_info "Die Raspberry Pi App wurde vollständig entfernt."
    echo ""
}

# Skript ausführen
main


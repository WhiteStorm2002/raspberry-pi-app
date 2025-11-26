#!/bin/bash
###############################################################################
# UPDATE-SKRIPT für Raspberry Pi Eingangsbereich Display
# 
# Dieses Skript aktualisiert die Anwendung auf eine neue Version
# 
# WICHTIG: Lies UPDATE_GUIDE.md für Details zum Update-Prozess!
#
# Verwendung: sudo ./update.sh
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
CONFIG_DIR="$HOME/.config/${APP_NAME}"
BACKUP_DIR="/tmp/${APP_NAME}_backup_$(date +%Y%m%d_%H%M%S)"
SERVICE_NAME="${APP_NAME}.service"
CURRENT_VERSION_FILE="${APP_DIR}/VERSION"
NEW_VERSION_FILE="./VERSION"

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

check_installation() {
    if [ ! -d "${APP_DIR}" ]; then
        print_error "Anwendung ist nicht installiert!"
        echo "Bitte führen Sie zuerst ./install.sh aus."
        exit 1
    fi
}

get_current_version() {
    if [ -f "${CURRENT_VERSION_FILE}" ]; then
        cat "${CURRENT_VERSION_FILE}"
    else
        echo "Unbekannt"
    fi
}

get_new_version() {
    if [ -f "${NEW_VERSION_FILE}" ]; then
        cat "${NEW_VERSION_FILE}"
    else
        echo "Unbekannt"
    fi
}

create_backup() {
    print_info "Erstelle Backup..."
    
    mkdir -p "${BACKUP_DIR}"
    
    # Backup der Anwendung
    if [ -d "${APP_DIR}" ]; then
        cp -r "${APP_DIR}" "${BACKUP_DIR}/app"
    fi
    
    # Backup der Konfiguration
    if [ -d "${CONFIG_DIR}" ]; then
        cp -r "${CONFIG_DIR}" "${BACKUP_DIR}/config"
    fi
    
    # Backup des Service
    if [ -f "/etc/systemd/system/${SERVICE_NAME}" ]; then
        cp "/etc/systemd/system/${SERVICE_NAME}" "${BACKUP_DIR}/"
    fi
    
    print_success "Backup erstellt: ${BACKUP_DIR}"
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

update_files() {
    print_info "Aktualisiere Dateien..."
    
    # Kopiere neue Dateien
    if [ -d "src" ]; then
        cp -r src/* "${APP_DIR}/"
        print_success "Python-Dateien aktualisiert"
    fi
    
    # Aktualisiere requirements.txt
    if [ -f "requirements.txt" ]; then
        cp requirements.txt "${APP_DIR}/"
        print_success "requirements.txt aktualisiert"
    fi
    
    # Aktualisiere setup.py
    if [ -f "setup.py" ]; then
        cp setup.py "${APP_DIR}/"
        print_success "setup.py aktualisiert"
    fi
}

update_dependencies() {
    print_info "Aktualisiere Python-Abhängigkeiten..."
    
    VENV_DIR="${APP_DIR}/venv"
    
    if [ -d "${VENV_DIR}" ]; then
        "${VENV_DIR}/bin/pip" install --upgrade pip
        "${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt" --upgrade
        print_success "Abhängigkeiten aktualisiert"
    else
        print_warning "Virtuelle Umgebung nicht gefunden!"
    fi
}

update_service() {
    print_info "Prüfe Service-Datei..."
    
    if [ -f "install.sh" ]; then
        # Service wird bei Bedarf durch install.sh aktualisiert
        # Hier nur prüfen ob Update nötig ist
        print_info "Service-Datei unverändert"
    fi
}

migrate_config() {
    print_info "Migriere Konfiguration..."
    
    # Lade alte Config
    CONFIG_FILE="${CONFIG_DIR}/config.json"
    
    if [ -f "${CONFIG_FILE}" ]; then
        # Prüfe ob neue Felder hinzugefügt werden müssen
        # Python-Skript zur Config-Migration
        python3 << EOF
import json
import sys

config_file = "${CONFIG_FILE}"

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Füge neue Felder hinzu falls nicht vorhanden
    updated = False
    
    # Migration für Version 1.3.0: Alte Felder zu neuem display_mode System
    if 'display_mode' not in config:
        # Migriere alte Konfiguration
        if config.get('time_control_enabled', False):
            config['display_mode'] = 'time'
        elif config.get('pir_enabled', True):
            config['display_mode'] = 'pir'
        else:
            config['display_mode'] = 'continuous'
        updated = True
        print("Config migriert: display_mode hinzugefügt")
    
    # Entferne alte Felder
    if 'time_control_enabled' in config:
        del config['time_control_enabled']
        updated = True
    
    if 'pir_enabled' in config:
        del config['pir_enabled']
        updated = True
    
    # Stelle sicher dass Zeitfelder existieren
    if 'work_start_time' not in config:
        config['work_start_time'] = "08:00"
        updated = True
    
    if 'work_end_time' not in config:
        config['work_end_time'] = "17:00"
        updated = True
    
    # Update Version
    if 'version' not in config:
        config['version'] = "1.4.0"
        updated = True
    else:
        config['version'] = "1.4.0"
        updated = True
    
    # Speichere wenn aktualisiert
    if updated:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print("Konfiguration migriert")
    else:
        print("Konfiguration aktuell")
    
except Exception as e:
    print(f"Fehler bei Config-Migration: {e}", file=sys.stderr)
    sys.exit(1)
EOF
        
        print_success "Konfiguration migriert"
    else
        print_info "Keine Konfiguration gefunden"
    fi
}

update_version() {
    print_info "Aktualisiere Versionsnummer..."
    
    if [ -f "${NEW_VERSION_FILE}" ]; then
        cp "${NEW_VERSION_FILE}" "${CURRENT_VERSION_FILE}"
        print_success "Version aktualisiert"
    fi
}

start_service() {
    print_info "Starte Service..."
    
    systemctl daemon-reload
    
    if systemctl is-enabled --quiet "${SERVICE_NAME}" 2>/dev/null; then
        systemctl start "${SERVICE_NAME}"
        print_success "Service gestartet"
    else
        print_info "Service ist nicht aktiviert (Autostart deaktiviert)"
    fi
}

rollback() {
    print_error "Update fehlgeschlagen! Führe Rollback durch..."
    
    if [ -d "${BACKUP_DIR}" ]; then
        # Restore App
        if [ -d "${BACKUP_DIR}/app" ]; then
            rm -rf "${APP_DIR}"
            cp -r "${BACKUP_DIR}/app" "${APP_DIR}"
        fi
        
        # Restore Config
        if [ -d "${BACKUP_DIR}/config" ]; then
            rm -rf "${CONFIG_DIR}"
            cp -r "${BACKUP_DIR}/config" "${CONFIG_DIR}"
        fi
        
        # Restore Service
        if [ -f "${BACKUP_DIR}/${SERVICE_NAME}" ]; then
            cp "${BACKUP_DIR}/${SERVICE_NAME}" "/etc/systemd/system/"
            systemctl daemon-reload
        fi
        
        print_success "Rollback abgeschlossen"
        
        # Starte alten Service
        if systemctl is-enabled --quiet "${SERVICE_NAME}" 2>/dev/null; then
            systemctl start "${SERVICE_NAME}"
        fi
    else
        print_error "Kein Backup gefunden!"
    fi
}

# Hauptprogramm
main() {
    echo "=========================================="
    echo "  Raspberry Pi App - UPDATE"
    echo "=========================================="
    echo ""
    
    check_root
    check_installation
    
    CURRENT_VERSION=$(get_current_version)
    NEW_VERSION=$(get_new_version)
    
    echo "Aktuelle Version: ${CURRENT_VERSION}"
    echo "Neue Version:     ${NEW_VERSION}"
    echo ""
    
    if [ "${CURRENT_VERSION}" = "${NEW_VERSION}" ]; then
        print_warning "Versionen sind identisch!"
        read -p "Trotzdem fortfahren? (j/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Jj]$ ]]; then
            exit 0
        fi
    fi
    
    echo ""
    read -p "Update durchführen? (j/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Jj]$ ]]; then
        print_info "Update abgebrochen."
        exit 0
    fi
    
    echo ""
    print_info "Starte Update-Prozess..."
    echo ""
    
    # Update-Prozess mit Fehlerbehandlung
    if create_backup && \
       stop_service && \
       update_files && \
       update_dependencies && \
       update_service && \
       migrate_config && \
       update_version && \
       start_service; then
        
        echo ""
        echo "=========================================="
        print_success "Update erfolgreich abgeschlossen!"
        echo "=========================================="
        echo ""
        echo "Neue Version: ${NEW_VERSION}"
        echo "Backup:       ${BACKUP_DIR}"
        echo ""
        echo "Das Backup kann gelöscht werden wenn alles funktioniert:"
        echo "  rm -rf ${BACKUP_DIR}"
        echo ""
        
    else
        echo ""
        rollback
        exit 1
    fi
}

# Fehlerbehandlung
trap 'rollback' ERR

# Skript ausführen
main


#!/bin/bash
###############################################################################
# Installer für Raspberry Pi App
# Dieses Skript installiert die Python-Anwendung auf dem Raspberry Pi
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
LOG_DIR="/var/log"
SERVICE_NAME="${APP_NAME}.service"
VENV_DIR="${APP_DIR}/venv"

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

check_raspberry_pi() {
    if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
        print_warning "Dieses System scheint kein Raspberry Pi zu sein!"
        read -p "Trotzdem fortfahren? (j/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Jj]$ ]]; then
            exit 1
        fi
    fi
}

check_dependencies() {
    print_info "Prüfe Abhängigkeiten..."
    
    # Python 3 prüfen
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 ist nicht installiert!"
        exit 1
    fi
    
    # pip prüfen
    if ! command -v pip3 &> /dev/null; then
        print_info "pip3 wird installiert..."
        apt-get update
        apt-get install -y python3-pip
    fi
    
    # venv prüfen
    if ! python3 -c "import venv" &> /dev/null; then
        print_info "python3-venv wird installiert..."
        apt-get install -y python3-venv
    fi
    
    # Tkinter prüfen und installieren
    if ! python3 -c "import tkinter" &> /dev/null; then
        print_info "python3-tk wird installiert..."
        apt-get install -y python3-tk
    fi
    
    # PIL/Pillow Abhängigkeiten
    print_info "Installiere Bildverarbeitungs-Bibliotheken..."
    apt-get install -y python3-pil python3-pil.imagetk libjpeg-dev zlib1g-dev
    
    print_success "Alle Abhängigkeiten sind vorhanden"
}

create_directories() {
    print_info "Erstelle Verzeichnisse..."
    
    mkdir -p "${APP_DIR}"
    mkdir -p "${CONFIG_DIR}"
    mkdir -p "${LOG_DIR}"
    
    print_success "Verzeichnisse erstellt"
}

install_app() {
    print_info "Installiere Anwendung..."
    
    # Kopiere Dateien
    cp -r src/* "${APP_DIR}/"
    cp requirements.txt "${APP_DIR}/" 2>/dev/null || true
    
    # Erstelle virtuelle Umgebung
    print_info "Erstelle virtuelle Python-Umgebung..."
    python3 -m venv "${VENV_DIR}"
    
    # Aktiviere venv und installiere Abhängigkeiten
    print_info "Installiere Python-Abhängigkeiten..."
    "${VENV_DIR}/bin/pip" install --upgrade pip setuptools wheel
    
    # Installiere Requirements einzeln (robuster)
    if [ -f "${APP_DIR}/requirements.txt" ]; then
        "${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt" || {
            print_warning "Einige Pakete konnten nicht installiert werden, versuche einzeln..."
            # Installiere nur die wichtigsten Pakete
            "${VENV_DIR}/bin/pip" install RPi.GPIO gpiozero Pillow || true
        }
    fi
    
    print_success "Anwendung installiert"
}

create_service() {
    print_info "Erstelle systemd Service..."
    
    # Ermittle den aktuellen Benutzer (falls nicht root)
    REAL_USER="${SUDO_USER:-pi}"
    USER_HOME=$(eval echo ~${REAL_USER})
    
    cat > "/etc/systemd/system/${SERVICE_NAME}" << EOF
[Unit]
Description=Raspberry Pi Eingangsbereich Display
After=graphical.target network.target
Wants=graphical.target

[Service]
Type=simple
User=${REAL_USER}
Environment="DISPLAY=:0"
Environment="XAUTHORITY=${USER_HOME}/.Xauthority"
Environment="PYTHONPATH=${APP_DIR}"
WorkingDirectory=${APP_DIR}
ExecStart=${VENV_DIR}/bin/python3 -m app.main
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=graphical.target
EOF

    # Service neu laden
    systemctl daemon-reload
    
    print_success "systemd Service erstellt"
}

setup_permissions() {
    print_info "Setze Berechtigungen..."
    
    chmod -R 755 "${APP_DIR}"
    chmod 644 "/etc/systemd/system/${SERVICE_NAME}"
    touch "${LOG_DIR}/${APP_NAME}.log"
    chmod 644 "${LOG_DIR}/${APP_NAME}.log"
    
    print_success "Berechtigungen gesetzt"
}

enable_service() {
    print_info "Aktiviere Service..."
    
    systemctl enable "${SERVICE_NAME}"
    
    print_success "Service aktiviert"
}

# Hauptprogramm
main() {
    echo "=========================================="
    echo "  Raspberry Pi App - Installer"
    echo "=========================================="
    echo ""
    
    check_root
    check_raspberry_pi
    check_dependencies
    create_directories
    install_app
    create_service
    setup_permissions
    enable_service
    
    echo ""
    echo "=========================================="
    print_success "Installation erfolgreich abgeschlossen!"
    echo "=========================================="
    echo ""
    echo "Nützliche Befehle:"
    echo "  Service starten:   sudo systemctl start ${SERVICE_NAME}"
    echo "  Service stoppen:   sudo systemctl stop ${SERVICE_NAME}"
    echo "  Service Status:    sudo systemctl status ${SERVICE_NAME}"
    echo "  Logs anzeigen:     sudo journalctl -u ${SERVICE_NAME} -f"
    echo "  Deinstallieren:    sudo ./uninstall.sh"
    echo ""
    
    read -p "Möchten Sie den Service jetzt starten? (j/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        systemctl start "${SERVICE_NAME}"
        print_success "Service gestartet!"
        echo ""
        systemctl status "${SERVICE_NAME}" --no-pager
    fi
}

# Skript ausführen
main


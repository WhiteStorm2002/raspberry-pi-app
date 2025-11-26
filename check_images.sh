#!/bin/bash
###############################################################################
# Prüft ob Bilder im konfigurierten Ordner vorhanden sind
###############################################################################

# Farben
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
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

print_warning() {
    echo -e "${YELLOW}[WARNUNG]${NC} $1"
}

echo "=========================================="
echo "  Bild-Ordner Prüfung"
echo "=========================================="
echo ""

# Lese Config
CONFIG_FILE="$HOME/.config/raspi-app/config.json"

if [ -f "$CONFIG_FILE" ]; then
    print_info "Lese Konfiguration..."
    IMAGE_FOLDER=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['image_folder'])" 2>/dev/null)
    
    if [ -z "$IMAGE_FOLDER" ]; then
        print_warning "Konnte Bildordner nicht aus Config lesen"
        IMAGE_FOLDER="$HOME/Pictures/slideshow"
    fi
else
    print_warning "Config nicht gefunden, verwende Standard"
    IMAGE_FOLDER="$HOME/Pictures/slideshow"
fi

echo "Bildordner: $IMAGE_FOLDER"
echo ""

# Prüfe ob Ordner existiert
if [ ! -d "$IMAGE_FOLDER" ]; then
    print_error "Ordner existiert nicht!"
    echo ""
    echo "Erstelle Ordner:"
    echo "  mkdir -p $IMAGE_FOLDER"
    exit 1
fi

print_success "Ordner existiert"
echo ""

# Zähle Bilder
print_info "Suche nach Bildern..."
echo ""

JPG_COUNT=$(find "$IMAGE_FOLDER" -maxdepth 1 -type f \( -iname "*.jpg" -o -iname "*.jpeg" \) 2>/dev/null | wc -l)
PNG_COUNT=$(find "$IMAGE_FOLDER" -maxdepth 1 -type f -iname "*.png" 2>/dev/null | wc -l)
GIF_COUNT=$(find "$IMAGE_FOLDER" -maxdepth 1 -type f -iname "*.gif" 2>/dev/null | wc -l)
BMP_COUNT=$(find "$IMAGE_FOLDER" -maxdepth 1 -type f -iname "*.bmp" 2>/dev/null | wc -l)
WEBP_COUNT=$(find "$IMAGE_FOLDER" -maxdepth 1 -type f -iname "*.webp" 2>/dev/null | wc -l)

TOTAL=$((JPG_COUNT + PNG_COUNT + GIF_COUNT + BMP_COUNT + WEBP_COUNT))

echo "Gefundene Bilder:"
echo "  JPG/JPEG: $JPG_COUNT"
echo "  PNG:      $PNG_COUNT"
echo "  GIF:      $GIF_COUNT"
echo "  BMP:      $BMP_COUNT"
echo "  WEBP:     $WEBP_COUNT"
echo "  ─────────────────"
echo "  GESAMT:   $TOTAL"
echo ""

if [ $TOTAL -eq 0 ]; then
    print_error "Keine Bilder gefunden!"
    echo ""
    echo "Lösungen:"
    echo "  1. Beispielbilder erstellen:"
    echo "     ./create_sample_images.sh"
    echo ""
    echo "  2. Eigene Bilder kopieren:"
    echo "     cp /pfad/zu/bildern/*.jpg $IMAGE_FOLDER/"
    echo ""
    echo "  3. Ordner in GUI ändern"
    exit 1
else
    print_success "$TOTAL Bilder gefunden!"
    echo ""
    echo "Liste der Bilder:"
    ls -lh "$IMAGE_FOLDER" | grep -E '\.(jpg|jpeg|png|gif|bmp|webp)$' -i
fi

echo ""
echo "=========================================="


#!/bin/bash
###############################################################################
# Erstellt Beispielbilder für die Slideshow
# Nützlich zum Testen der Anwendung
###############################################################################

# Farben
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

# Bildordner
IMAGE_DIR="$HOME/Pictures/slideshow"

print_info "Erstelle Beispielbilder in ${IMAGE_DIR}..."

# Erstelle Verzeichnis
mkdir -p "${IMAGE_DIR}"

# Erstelle einfache Testbilder mit ImageMagick (falls verfügbar)
if command -v convert &> /dev/null; then
    print_info "Erstelle Testbilder mit ImageMagick..."
    
    convert -size 1920x1080 xc:blue -pointsize 100 -fill white -gravity center \
        -annotate +0+0 "Willkommen!\nBild 1" "${IMAGE_DIR}/bild1.png"
    
    convert -size 1920x1080 xc:green -pointsize 100 -fill white -gravity center \
        -annotate +0+0 "Eingangsbereich\nBild 2" "${IMAGE_DIR}/bild2.png"
    
    convert -size 1920x1080 xc:red -pointsize 100 -fill white -gravity center \
        -annotate +0+0 "Raspberry Pi\nBild 3" "${IMAGE_DIR}/bild3.png"
    
    convert -size 1920x1080 xc:purple -pointsize 100 -fill white -gravity center \
        -annotate +0+0 "Display System\nBild 4" "${IMAGE_DIR}/bild4.png"
    
    print_success "Beispielbilder erstellt!"
else
    print_info "ImageMagick nicht gefunden. Bitte fügen Sie manuell Bilder hinzu."
    echo ""
    echo "Legen Sie Ihre Bilder (JPG, PNG, etc.) in folgendem Ordner ab:"
    echo "  ${IMAGE_DIR}"
fi

echo ""
echo "Bildordner: ${IMAGE_DIR}"
echo "Anzahl Bilder: $(find "${IMAGE_DIR}" -type f \( -iname "*.jpg" -o -iname "*.png" -o -iname "*.gif" \) 2>/dev/null | wc -l)"
echo ""


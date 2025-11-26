#!/usr/bin/env python3
"""
Test-Skript: Prüft ob Bilder gefunden werden
"""

import sys
from pathlib import Path

# Füge src zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from app.config import ConfigManager
from app.slideshow import Slideshow

def main():
    print("\n" + "="*60)
    print("🔍 BILD-SUCHE TEST")
    print("="*60 + "\n")
    
    # Lade Config
    config_manager = ConfigManager()
    config = config_manager.get()
    
    print(f"Konfigurierter Bildordner: {config.image_folder}")
    print(f"Ordner existiert: {Path(config.image_folder).exists()}")
    print()
    
    # Prüfe Ordner-Inhalt
    image_folder = Path(config.image_folder)
    if image_folder.exists():
        print("Alle Dateien im Ordner:")
        for file in sorted(image_folder.iterdir()):
            if file.is_file():
                print(f"  - {file.name} ({file.suffix})")
        print()
    else:
        print(f"❌ Ordner existiert nicht: {image_folder}\n")
        return
    
    # Teste Slideshow
    print("Starte Slideshow-Klasse...")
    slideshow = Slideshow(config.image_folder, config.random_order)
    
    print(f"\n✅ Gefundene Bilder: {slideshow.get_image_count()}")
    
    if slideshow.get_image_count() > 0:
        print("\nBilderliste:")
        for i, img in enumerate(slideshow.images, 1):
            print(f"  {i}. {img.name}")
    else:
        print("\n❌ Keine Bilder gefunden!")
        print(f"\nUnterstützte Formate: {', '.join(Slideshow.SUPPORTED_FORMATS)}")
        print(f"\nPrüfe ob Dateien diese Endungen haben:")
        for file in image_folder.iterdir():
            if file.is_file():
                print(f"  {file.name} → Endung: {file.suffix}")
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()


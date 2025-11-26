#!/usr/bin/env python3
"""
Debug-Skript zum Testen der GUI ohne Slideshow
Zeigt genau was beim START-Button passiert
"""

import sys
import logging
from pathlib import Path

# Füge src zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Logging konfigurieren
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_callback():
    """Test-Callback für START-Button"""
    print("\n" + "="*60)
    print("✅ CALLBACK WURDE AUFGERUFEN!")
    print("="*60)
    logger.info("START-Button Callback wurde erfolgreich aufgerufen!")
    print("\nDie Slideshow würde jetzt starten...")
    print("Drücke STRG+C zum Beenden")
    print("="*60 + "\n")

def main():
    """Hauptfunktion"""
    print("\n" + "="*60)
    print("🐛 DEBUG-MODUS: GUI-Test")
    print("="*60)
    print("\nDieses Skript testet nur die GUI ohne Slideshow.")
    print("Wenn du auf START klickst, wird nur eine Meldung angezeigt.\n")
    
    try:
        from app.config import ConfigManager
        from app.gui import ConfigGUI
        
        # Erstelle Config-Manager
        config_manager = ConfigManager()
        
        # Erstelle GUI mit Test-Callback
        gui = ConfigGUI(
            config_manager=config_manager,
            on_start_callback=test_callback
        )
        
        print("✅ GUI erstellt")
        print("\nAnweisungen:")
        print("1. Klicke auf 'Speichern' → Sollte Messagebox zeigen")
        print("2. Klicke auf 'START' → Sollte KEINE Messagebox zeigen")
        print("3. Prüfe ob Callback aufgerufen wird (siehe Terminal)")
        print("\n" + "="*60 + "\n")
        
        # Starte GUI
        gui.run()
        
    except Exception as e:
        logger.error(f"Fehler: {e}", exc_info=True)
        print(f"\n❌ Fehler: {e}\n")

if __name__ == '__main__':
    main()


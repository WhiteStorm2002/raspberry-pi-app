#!/usr/bin/env python3
"""
Hauptanwendung für Raspberry Pi Eingangsbereich Display
Diese Anwendung zeigt eine Slideshow mit PIR-Bewegungssensor-Steuerung
"""

import sys
import signal
import logging
from pathlib import Path

from .config import ConfigManager
from .gui import ConfigGUI
from .slideshow_window import SlideshowWindow
from .error_logger import get_error_logger, setup_crash_handler
from .sensor_detector import get_sensor_detector

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Richte Crash-Handler ein
setup_crash_handler()


class EntranceDisplayApp:
    """Hauptklasse für die Eingangsbereich Display Anwendung"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config_gui = None
        self.slideshow_window = None
        self.running = False
        self.error_logger = get_error_logger()
        self.sensor_detector = get_sensor_detector()
        
        logger.info("Eingangsbereich Display App wird initialisiert...")
        
        # Prüfe Sensor-Verfügbarkeit
        pir_available = self.sensor_detector.is_pir_available()
        logger.info(f"PIR-Sensor verfügbar: {pir_available}")
        
        # Cleanup alte Logs (beim Start)
        try:
            self.error_logger.cleanup_old_logs(days=30)
        except Exception as e:
            logger.warning(f"Fehler beim Log-Cleanup: {e}")
    
    def setup(self):
        """Initialisierung der Anwendung"""
        try:
            # Erstelle Bildordner falls nicht vorhanden
            config = self.config_manager.get()
            image_folder = Path(config.image_folder)
            if not image_folder.exists():
                image_folder.mkdir(parents=True, exist_ok=True)
                logger.info(f"Bildordner erstellt: {image_folder}")
            
            # GUI erstellen
            self.config_gui = ConfigGUI(
                config_manager=self.config_manager,
                on_start_callback=self._start_slideshow
            )
            
            logger.info("Setup abgeschlossen")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Setup: {e}")
            # Log Error
            self.error_logger.log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                traceback_str=None,
                context={'phase': 'setup'}
            )
            return False
    
    def _start_slideshow(self):
        """Startet die Slideshow"""
        try:
            logger.info("Starte Slideshow...")
            
            # Lade aktuelle Konfiguration (neu laden!)
            config = self.config_manager.get()
            logger.info(f"Config geladen: Modus={config.display_mode}, Bilder={config.image_folder}")
            
            # Prüfe ob Modus verfügbar ist (nur für PIR-abhängige Modi)
            if config.display_mode in ["pir", "time_pir"]:
                # Nur bei PIR-Modi prüfen ob Sensor verfügbar ist
                if not self.sensor_detector.is_pir_available():
                    logger.error(f"Modus '{config.display_mode}' benötigt PIR-Sensor!")
                    from tkinter import messagebox
                    messagebox.showerror(
                        "Fehler",
                        f"Modus '{config.display_mode}' kann nicht gestartet werden!\n\n"
                        f"Grund: PIR-Sensor nicht verfügbar.\n"
                        f"Bitte wähle Modus 2 (Zeit) oder Modus 3 (24/7)."
                    )
                    self.config_gui.show()
                    return
            
            # Erstelle Slideshow-Fenster NEU (mit aktueller Config!)
            logger.info("Erstelle Slideshow-Fenster...")
            self.slideshow_window = SlideshowWindow(
                config=config,
                on_exit_callback=self._stop_slideshow
            )
            
            logger.info("Slideshow-Fenster erstellt")
            
            # Verstecke Config-GUI
            logger.info("Verstecke Config-GUI...")
            self.config_gui.hide()
            
            # Starte Slideshow (zeigt Fenster automatisch)
            logger.info("Starte Slideshow...")
            self.slideshow_window.start()
            
            logger.info("Slideshow erfolgreich gestartet!")
            
            # Force update um sicherzustellen dass Fenster angezeigt wird
            self.slideshow_window.root.update()
            self.slideshow_window.root.update_idletasks()
            
        except Exception as e:
            logger.error(f"Fehler beim Starten der Slideshow: {e}")
            # Log Error
            import traceback
            self.error_logger.log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                traceback_str=traceback.format_exc(),
                context={'phase': 'start_slideshow'}
            )
            self.config_gui.show()
    
    def _stop_slideshow(self):
        """Stoppt die Slideshow und zeigt Config-GUI"""
        try:
            logger.info("Stoppe Slideshow...")
            
            if self.slideshow_window:
                self.slideshow_window.stop()
                self.slideshow_window.hide()
            
            # Zeige Config-GUI
            self.config_gui.show()
            
            logger.info("Slideshow gestoppt")
            
        except Exception as e:
            logger.error(f"Fehler beim Stoppen der Slideshow: {e}")
    
    def run(self):
        """Hauptschleife der Anwendung"""
        self.running = True
        logger.info("Anwendung gestartet")
        
        try:
            # Prüfe ob Autostart aktiviert ist
            config = self.config_manager.get()
            if config.autostart:
                logger.info("Autostart aktiviert - starte Slideshow automatisch")
                # Verzögert starten damit GUI Zeit hat sich zu initialisieren
                self.config_gui.root.after(1000, self._start_slideshow)
            
            # Starte GUI-Hauptschleife
            self.config_gui.run()
            
        except KeyboardInterrupt:
            logger.info("Anwendung wird durch Benutzer beendet...")
        except Exception as e:
            logger.error(f"Fehler in der Hauptschleife: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Aufräumen und Ressourcen freigeben"""
        logger.info("Cleanup wird durchgeführt...")
        self.running = False
        
        if self.slideshow_window:
            self.slideshow_window.stop()
        
        # Zeige Fehler-Statistiken
        try:
            stats = self.error_logger.get_statistics()
            if stats['crash_reports'] > 0 or stats['error_reports'] > 0:
                logger.info(f"Fehler-Statistiken: {stats['crash_reports']} Crashes, "
                          f"{stats['error_reports']} Errors, "
                          f"{stats['unique_errors']} eindeutige Fehler")
                logger.info(f"Log-Verzeichnis: {stats['log_directory']}")
        except Exception:
            pass
        
        logger.info("Anwendung beendet")
    
    def stop(self):
        """Anwendung stoppen"""
        logger.info("Stop-Signal empfangen")
        self.running = False


def signal_handler(signum, frame):
    """Signal-Handler für sauberes Beenden"""
    logger.info(f"Signal {signum} empfangen")
    sys.exit(0)


def main():
    """Haupteinstiegspunkt der Anwendung"""
    # Signal-Handler registrieren
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=" * 60)
    logger.info("Raspberry Pi Eingangsbereich Display v1.0.0")
    logger.info("=" * 60)
    
    # App erstellen und starten
    app = EntranceDisplayApp()
    
    if app.setup():
        app.run()
    else:
        logger.error("Setup fehlgeschlagen. Anwendung wird beendet.")
        sys.exit(1)


if __name__ == '__main__':
    main()

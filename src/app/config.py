#!/usr/bin/env python3
"""
Konfigurationsverwaltung für die Raspberry Pi Eingangsbereich App
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, asdict

# Pfade
APP_NAME = 'raspi-app'
APP_DIR = Path('/opt') / APP_NAME
CONFIG_DIR = Path.home() / '.config' / APP_NAME
CONFIG_FILE = CONFIG_DIR / 'config.json'
LOG_DIR = Path('/var/log')
SERVICE_FILE = Path('/etc/systemd/system') / f'{APP_NAME}.service'

# Stelle sicher, dass Config-Verzeichnis existiert
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class AppConfig:
    """Konfigurationsklasse für die Anwendung"""
    
    # Display-Modi (nur EINER kann aktiv sein!)
    # Modus 1: PIR-Steuerung (Bewegungssensor)
    # Modus 2: Zeitsteuerung (Arbeitszeit/Feierabend)
    # Modus 3: Dauerschleife (24/7 immer an)
    # Modus 4: Zeitsteuerung + PIR (Arbeitszeit: Dauerschleife, Feierabend: PIR)
    display_mode: str = "pir"  # "pir", "time", "continuous", "time_pir"
    
    # PIR Sensor (nur wenn display_mode == "pir")
    pir_pin: int = 4  # GPIO Pin für PIR Sensor
    screen_timeout: int = 120  # Sekunden bis Bildschirm ausgeht (2 Minuten)
    
    # Zeitsteuerung (nur wenn display_mode == "time")
    work_start_time: str = "08:00"  # Arbeitsbeginn
    work_end_time: str = "17:00"    # Feierabend
    # Während Arbeitszeit: Dauerschleife ohne PIR
    # Außerhalb Arbeitszeit: Bildschirm AUS
    
    # Bilder
    image_folder: str = str(Path.home() / 'Pictures' / 'slideshow')
    image_duration: int = 5  # Sekunden pro Bild
    random_order: bool = False  # False = Liste, True = Zufällig
    
    # System
    autostart: bool = True
    fullscreen: bool = True
    hide_cursor: bool = True  # Mauszeiger in Slideshow verstecken
    
    # Debug
    debug_mode: bool = False
    show_sensor_status: bool = True
    
    # Version
    version: str = "1.4.0"


class ConfigManager:
    """Verwaltet die Konfiguration"""
    
    def __init__(self):
        self.config = self.load()
    
    def load(self) -> AppConfig:
        """Lädt die Konfiguration aus der Datei"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return AppConfig(**data)
            except Exception as e:
                print(f"Fehler beim Laden der Konfiguration: {e}")
                return AppConfig()
        else:
            # Erstelle Standard-Konfiguration
            config = AppConfig()
            self.save(config)
            return config
    
    def save(self, config: AppConfig) -> bool:
        """Speichert die Konfiguration in die Datei"""
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(asdict(config), f, indent=2)
            return True
        except Exception as e:
            print(f"Fehler beim Speichern der Konfiguration: {e}")
            return False
    
    def get(self) -> AppConfig:
        """Gibt die aktuelle Konfiguration zurück"""
        return self.config
    
    def update(self, **kwargs) -> bool:
        """Aktualisiert die Konfiguration"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        return self.save(self.config)
    
    def validate_display_mode(self, mode: str) -> bool:
        """
        Validiert den Display-Modus
        
        Args:
            mode: Display-Modus ("pir", "time", "continuous", "time_pir")
            
        Returns:
            True wenn gültig
        """
        return mode in ["pir", "time", "continuous", "time_pir"]

#!/usr/bin/env python3
"""
PIR Motion Sensor Verwaltung
"""

import logging
from typing import Callable, Optional
import threading
import time

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    print("WARNUNG: RPi.GPIO nicht verfügbar - Sensor-Simulation aktiv")

logger = logging.getLogger(__name__)


class PIRSensor:
    """Klasse für PIR Motion Sensor"""
    
    def __init__(self, pin: int, callback: Optional[Callable] = None):
        """
        Initialisiert den PIR Sensor
        
        Args:
            pin: GPIO Pin-Nummer (BCM)
            callback: Funktion die bei Bewegung aufgerufen wird
        """
        self.pin = pin
        self.callback = callback
        self.enabled = False
        self.motion_detected = False
        self.last_motion_time = 0
        self._monitoring = False
        self._monitor_thread = None
        self.initialization_failed = False
        
        if GPIO_AVAILABLE:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                logger.info(f"PIR Sensor initialisiert auf Pin {self.pin}")
            except Exception as e:
                logger.error(f"Fehler beim Initialisieren des PIR Sensors: {e}")
                self.initialization_failed = True
        else:
            logger.warning("PIR Sensor im Simulationsmodus")
            self.initialization_failed = True
    
    def start_monitoring(self):
        """Startet die Überwachung des Sensors"""
        if self._monitoring:
            return
        
        self.enabled = True
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("PIR Sensor Überwachung gestartet")
    
    def stop_monitoring(self):
        """Stoppt die Überwachung des Sensors"""
        self.enabled = False
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
        logger.info("PIR Sensor Überwachung gestoppt")
    
    def _monitor_loop(self):
        """Überwachungsschleife für den Sensor"""
        while self._monitoring:
            try:
                if GPIO_AVAILABLE:
                    # Lese GPIO Pin
                    state = GPIO.input(self.pin)
                    
                    if state == GPIO.HIGH and not self.motion_detected:
                        # Bewegung erkannt
                        self.motion_detected = True
                        self.last_motion_time = time.time()
                        logger.info("Bewegung erkannt!")
                        
                        if self.callback:
                            self.callback(True)
                    
                    elif state == GPIO.LOW and self.motion_detected:
                        # Keine Bewegung mehr
                        self.motion_detected = False
                        logger.info("Keine Bewegung mehr")
                        
                        if self.callback:
                            self.callback(False)
                
                time.sleep(0.1)  # 100ms Polling-Intervall
                
            except Exception as e:
                logger.error(f"Fehler in der Sensor-Überwachung: {e}")
                time.sleep(1)
    
    def is_motion_detected(self) -> bool:
        """Gibt zurück ob aktuell Bewegung erkannt wird"""
        return self.motion_detected
    
    def get_last_motion_time(self) -> float:
        """Gibt den Zeitpunkt der letzten Bewegung zurück"""
        return self.last_motion_time
    
    def cleanup(self):
        """Räumt die GPIO-Ressourcen auf"""
        self.stop_monitoring()
        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup(self.pin)
                logger.info("PIR Sensor GPIO aufgeräumt")
            except Exception as e:
                logger.error(f"Fehler beim GPIO Cleanup: {e}")


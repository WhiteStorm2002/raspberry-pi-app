#!/usr/bin/env python3
"""
Sensor-Erkennung für PIR Motion Sensor
Prüft ob ein PIR-Sensor verfügbar ist
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False


class SensorDetector:
    """Erkennt verfügbare Sensoren"""
    
    def __init__(self):
        self._pir_available: Optional[bool] = None
        logger.info("SensorDetector initialisiert")
    
    def is_pir_available(self, pin: int = 4) -> bool:
        """
        Prüft ob ein PIR-Sensor verfügbar ist
        
        Args:
            pin: GPIO Pin zum Testen (Standard: 4)
            
        Returns:
            True wenn PIR-Sensor verfügbar ist
        """
        # Cache-Check
        if self._pir_available is not None:
            return self._pir_available
        
        # Prüfe ob GPIO verfügbar ist
        if not GPIO_AVAILABLE:
            logger.warning("RPi.GPIO nicht verfügbar - PIR-Sensor nicht nutzbar")
            self._pir_available = False
            return False
        
        # Prüfe ob auf Raspberry Pi
        if not self._is_raspberry_pi():
            logger.warning("Kein Raspberry Pi erkannt - PIR-Sensor nicht nutzbar")
            self._pir_available = False
            return False
        
        # Versuche GPIO zu initialisieren
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            
            # Teste ob Pin lesbar ist
            _ = GPIO.input(pin)
            
            # Cleanup
            GPIO.cleanup(pin)
            
            logger.info(f"PIR-Sensor auf Pin {pin} erkannt und verfügbar")
            self._pir_available = True
            return True
            
        except Exception as e:
            logger.warning(f"PIR-Sensor nicht verfügbar: {e}")
            self._pir_available = False
            return False
    
    def _is_raspberry_pi(self) -> bool:
        """Prüft ob das System ein Raspberry Pi ist"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
        except FileNotFoundError:
            return False
    
    def get_available_modes(self) -> list:
        """
        Gibt eine Liste der verfügbaren Display-Modi zurück
        
        Returns:
            Liste mit verfügbaren Modi
        """
        available_modes = []
        
        # Modus 1: PIR - nur wenn Sensor verfügbar
        if self.is_pir_available():
            available_modes.append("pir")
        
        # Modus 2: Zeit - immer verfügbar
        available_modes.append("time")
        
        # Modus 3: Dauerschleife - immer verfügbar
        available_modes.append("continuous")
        
        # Modus 4: Zeit+PIR - nur wenn Sensor verfügbar
        if self.is_pir_available():
            available_modes.append("time_pir")
        
        return available_modes
    
    def get_sensor_status_message(self) -> str:
        """
        Gibt eine Status-Nachricht über verfügbare Sensoren zurück
        
        Returns:
            Status-Nachricht als String
        """
        if not GPIO_AVAILABLE:
            return "⚠️ RPi.GPIO nicht installiert - PIR-Modi deaktiviert"
        
        if not self._is_raspberry_pi():
            return "⚠️ Kein Raspberry Pi - PIR-Modi deaktiviert"
        
        if self.is_pir_available():
            return "✅ PIR-Sensor verfügbar - Alle Modi aktiv"
        else:
            return "⚠️ PIR-Sensor nicht erkannt - PIR-Modi deaktiviert"


# Globale Instanz
_sensor_detector: Optional[SensorDetector] = None


def get_sensor_detector() -> SensorDetector:
    """Gibt die globale SensorDetector-Instanz zurück"""
    global _sensor_detector
    if _sensor_detector is None:
        _sensor_detector = SensorDetector()
    return _sensor_detector


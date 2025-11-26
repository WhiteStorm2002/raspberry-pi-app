#!/usr/bin/env python3
"""
Bildschirm-Steuerung für HDMI Display
"""

import subprocess
import logging
import os
import time

logger = logging.getLogger(__name__)


class ScreenController:
    """Klasse zur Steuerung des HDMI-Bildschirms"""
    
    def __init__(self):
        self.is_on = True
        self.last_command_time = 0
        logger.info("ScreenController initialisiert")
    
    def turn_on(self) -> bool:
        """Schaltet den Bildschirm ein"""
        try:
            # Verhindere zu häufige Befehle
            current_time = time.time()
            if current_time - self.last_command_time < 1:
                return True
            
            self.last_command_time = current_time
            
            # HDMI einschalten
            # Methode 1: vcgencmd (Raspberry Pi spezifisch)
            result = subprocess.run(
                ['vcgencmd', 'display_power', '1'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Methode 2: xset (für X11)
            if os.environ.get('DISPLAY'):
                subprocess.run(
                    ['xset', 'dpms', 'force', 'on'],
                    capture_output=True,
                    timeout=5
                )
            
            self.is_on = True
            logger.info("Bildschirm eingeschaltet")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Timeout beim Einschalten des Bildschirms")
            return False
        except FileNotFoundError:
            logger.warning("vcgencmd nicht gefunden - möglicherweise kein Raspberry Pi")
            self.is_on = True
            return True
        except Exception as e:
            logger.error(f"Fehler beim Einschalten des Bildschirms: {e}")
            return False
    
    def turn_off(self) -> bool:
        """Schaltet den Bildschirm aus"""
        try:
            # Verhindere zu häufige Befehle
            current_time = time.time()
            if current_time - self.last_command_time < 1:
                return True
            
            self.last_command_time = current_time
            
            # HDMI ausschalten
            # Methode 1: vcgencmd (Raspberry Pi spezifisch)
            result = subprocess.run(
                ['vcgencmd', 'display_power', '0'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Methode 2: xset (für X11)
            if os.environ.get('DISPLAY'):
                subprocess.run(
                    ['xset', 'dpms', 'force', 'off'],
                    capture_output=True,
                    timeout=5
                )
            
            self.is_on = False
            logger.info("Bildschirm ausgeschaltet")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Timeout beim Ausschalten des Bildschirms")
            return False
        except FileNotFoundError:
            logger.warning("vcgencmd nicht gefunden - möglicherweise kein Raspberry Pi")
            self.is_on = False
            return True
        except Exception as e:
            logger.error(f"Fehler beim Ausschalten des Bildschirms: {e}")
            return False
    
    def get_status(self) -> bool:
        """Gibt den aktuellen Status des Bildschirms zurück"""
        return self.is_on
    
    def toggle(self) -> bool:
        """Schaltet den Bildschirm um (ein/aus)"""
        if self.is_on:
            return self.turn_off()
        else:
            return self.turn_on()


#!/usr/bin/env python3
"""
Zeitsteuerung für Arbeitszeit-Modus
"""

import logging
from datetime import datetime, time
from typing import Tuple

logger = logging.getLogger(__name__)


class TimeController:
    """Verwaltet die Zeitsteuerung für Arbeitszeit/Feierabend"""
    
    def __init__(self, enabled: bool = False, 
                 work_start: str = "08:00", 
                 work_end: str = "17:00"):
        """
        Initialisiert den TimeController
        
        Args:
            enabled: Zeitsteuerung aktiviert
            work_start: Arbeitsbeginn (Format: "HH:MM")
            work_end: Feierabend (Format: "HH:MM")
        """
        self.enabled = enabled
        self.work_start = self._parse_time(work_start)
        self.work_end = self._parse_time(work_end)
        
        logger.info(f"TimeController initialisiert: {work_start} - {work_end}, Aktiviert: {enabled}")
    
    def _parse_time(self, time_str: str) -> time:
        """
        Parst einen Zeit-String zu einem time-Objekt
        
        Args:
            time_str: Zeit als String (Format: "HH:MM")
            
        Returns:
            time-Objekt
        """
        try:
            hours, minutes = map(int, time_str.split(':'))
            return time(hour=hours, minute=minutes)
        except Exception as e:
            logger.error(f"Fehler beim Parsen der Zeit '{time_str}': {e}")
            return time(hour=8, minute=0)  # Fallback
    
    def is_work_time(self) -> bool:
        """
        Prüft ob aktuell Arbeitszeit ist
        
        Returns:
            True wenn Arbeitszeit, False sonst
        """
        if not self.enabled:
            return False
        
        current_time = datetime.now().time()
        
        # Normale Arbeitszeit (z.B. 08:00 - 17:00)
        if self.work_start < self.work_end:
            is_work = self.work_start <= current_time <= self.work_end
        # Nachtschicht (z.B. 22:00 - 06:00)
        else:
            is_work = current_time >= self.work_start or current_time <= self.work_end
        
        return is_work
    
    def should_use_pir(self) -> bool:
        """
        Gibt zurück ob PIR-Sensor verwendet werden soll
        
        Returns:
            True wenn PIR verwendet werden soll (Feierabend oder deaktiviert)
            False wenn Dauerschleife (Arbeitszeit)
        """
        if not self.enabled:
            # Zeitsteuerung deaktiviert -> immer PIR verwenden
            return True
        
        # Während Arbeitszeit: KEINE PIR-Steuerung (Dauerschleife)
        # Außerhalb Arbeitszeit: PIR-Steuerung aktiv
        return not self.is_work_time()
    
    def get_mode_description(self) -> str:
        """
        Gibt eine Beschreibung des aktuellen Modus zurück
        
        Returns:
            Beschreibung als String
        """
        if not self.enabled:
            return "Zeitsteuerung deaktiviert - PIR-Modus aktiv"
        
        if self.is_work_time():
            return f"ARBEITSZEIT ({self.work_start.strftime('%H:%M')}-{self.work_end.strftime('%H:%M')}) - Dauerschleife aktiv"
        else:
            return f"FEIERABEND - PIR-Modus aktiv (Arbeitszeit: {self.work_start.strftime('%H:%M')}-{self.work_end.strftime('%H:%M')})"
    
    def get_next_mode_change(self) -> Tuple[str, str]:
        """
        Gibt den Zeitpunkt des nächsten Moduswechsels zurück
        
        Returns:
            Tuple (Zeit, Modus) z.B. ("08:00", "Arbeitszeit beginnt")
        """
        if not self.enabled:
            return ("--:--", "Zeitsteuerung deaktiviert")
        
        if self.is_work_time():
            return (self.work_end.strftime('%H:%M'), "Feierabend - PIR aktiviert")
        else:
            return (self.work_start.strftime('%H:%M'), "Arbeitsbeginn - Dauerschleife")
    
    def update_times(self, work_start: str, work_end: str):
        """
        Aktualisiert die Arbeitszeiten
        
        Args:
            work_start: Neue Startzeit
            work_end: Neue Endzeit
        """
        self.work_start = self._parse_time(work_start)
        self.work_end = self._parse_time(work_end)
        logger.info(f"Arbeitszeiten aktualisiert: {work_start} - {work_end}")
    
    def set_enabled(self, enabled: bool):
        """
        Aktiviert/Deaktiviert die Zeitsteuerung
        
        Args:
            enabled: True zum Aktivieren, False zum Deaktivieren
        """
        self.enabled = enabled
        logger.info(f"Zeitsteuerung {'aktiviert' if enabled else 'deaktiviert'}")


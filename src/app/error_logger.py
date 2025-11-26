#!/usr/bin/env python3
"""
Intelligentes Error-Logging-System mit Crash-Reports
Verhindert Log-Spam durch Rate-Limiting und intelligente Gruppierung
"""

import sys
import os
import logging
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import json
import hashlib

logger = logging.getLogger(__name__)


class ErrorLogger:
    """Verwaltet Fehlerprotokolle und Crash-Reports"""
    
    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialisiert den ErrorLogger
        
        Args:
            log_dir: Verzeichnis für Logs (Standard: ~/.local/share/raspi-app/logs)
        """
        if log_dir is None:
            log_dir = Path.home() / '.local' / 'share' / 'raspi-app' / 'logs'
        
        self.log_dir = log_dir
        self.crash_dir = log_dir / 'crashes'
        self.error_dir = log_dir / 'errors'
        
        # Erstelle Verzeichnisse
        self.crash_dir.mkdir(parents=True, exist_ok=True)
        self.error_dir.mkdir(parents=True, exist_ok=True)
        
        # Error-Tracking für Rate-Limiting
        self.error_cache: Dict[str, dict] = {}
        self.error_cache_file = log_dir / 'error_cache.json'
        
        # Lade Error-Cache
        self._load_error_cache()
        
        logger.info(f"ErrorLogger initialisiert: {log_dir}")
    
    def _load_error_cache(self):
        """Lädt den Error-Cache aus der Datei"""
        try:
            if self.error_cache_file.exists():
                with open(self.error_cache_file, 'r') as f:
                    self.error_cache = json.load(f)
                # Entferne alte Einträge (älter als 24 Stunden)
                self._cleanup_cache()
        except Exception as e:
            logger.warning(f"Fehler beim Laden des Error-Cache: {e}")
            self.error_cache = {}
    
    def _save_error_cache(self):
        """Speichert den Error-Cache in die Datei"""
        try:
            with open(self.error_cache_file, 'w') as f:
                json.dump(self.error_cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Fehler beim Speichern des Error-Cache: {e}")
    
    def _cleanup_cache(self):
        """Entfernt alte Cache-Einträge"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        cutoff_timestamp = cutoff_time.timestamp()
        
        # Entferne alte Einträge
        keys_to_remove = []
        for key, data in self.error_cache.items():
            if data.get('last_occurrence', 0) < cutoff_timestamp:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.error_cache[key]
    
    def _get_error_hash(self, error_type: str, error_message: str, 
                        traceback_str: Optional[str] = None) -> str:
        """
        Erstellt einen Hash für einen Fehler zur Identifikation
        
        Args:
            error_type: Fehlertyp (z.B. "ValueError")
            error_message: Fehlermeldung
            traceback_str: Traceback (optional)
            
        Returns:
            Hash-String
        """
        # Verwende nur die ersten 2 Zeilen des Tracebacks für Hash
        # (um ähnliche Fehler zu gruppieren)
        trace_lines = []
        if traceback_str:
            lines = traceback_str.split('\n')
            # Nehme nur relevante Zeilen (nicht die komplette Stack-Trace)
            for line in lines:
                if 'File "' in line or 'line ' in line:
                    trace_lines.append(line.strip())
                    if len(trace_lines) >= 2:
                        break
        
        hash_input = f"{error_type}:{error_message}:{':'.join(trace_lines)}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    def _should_log_error(self, error_hash: str) -> bool:
        """
        Prüft ob ein Fehler geloggt werden soll (Rate-Limiting)
        
        Args:
            error_hash: Hash des Fehlers
            
        Returns:
            True wenn Fehler geloggt werden soll
        """
        now = datetime.now().timestamp()
        
        if error_hash not in self.error_cache:
            # Neuer Fehler -> immer loggen
            self.error_cache[error_hash] = {
                'first_occurrence': now,
                'last_occurrence': now,
                'count': 1,
                'last_logged': now
            }
            self._save_error_cache()
            return True
        
        error_data = self.error_cache[error_hash]
        error_data['count'] += 1
        error_data['last_occurrence'] = now
        
        # Rate-Limiting-Regeln:
        # 1. Ersten 3 Vorkommen immer loggen
        if error_data['count'] <= 3:
            error_data['last_logged'] = now
            self._save_error_cache()
            return True
        
        # 2. Danach nur alle 5 Minuten
        time_since_last_log = now - error_data.get('last_logged', 0)
        if time_since_last_log > 300:  # 5 Minuten
            error_data['last_logged'] = now
            self._save_error_cache()
            return True
        
        # 3. Nicht loggen (zu häufig)
        self._save_error_cache()
        return False
    
    def log_crash(self, exception: Exception, context: Optional[Dict] = None):
        """
        Loggt einen Crash mit vollständigen Details
        
        Args:
            exception: Die Exception
            context: Zusätzlicher Kontext (optional)
        """
        timestamp = datetime.now()
        filename = f"crash-{timestamp.strftime('%Y%m%d-%H%M%S')}.md"
        filepath = self.crash_dir / filename
        
        # Sammle Informationen
        exc_type = type(exception).__name__
        exc_message = str(exception)
        exc_traceback = ''.join(traceback.format_exception(
            type(exception), exception, exception.__traceback__
        ))
        
        # Erstelle Crash-Report
        report = self._create_crash_report(
            timestamp=timestamp,
            exc_type=exc_type,
            exc_message=exc_message,
            exc_traceback=exc_traceback,
            context=context
        )
        
        # Speichere Report
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.critical(f"Crash-Report erstellt: {filepath}")
            print(f"\n{'='*60}")
            print(f"💥 CRASH DETECTED!")
            print(f"{'='*60}")
            print(f"Crash-Report: {filepath}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Crash-Reports: {e}")
    
    def log_error(self, error_type: str, error_message: str, 
                  traceback_str: Optional[str] = None,
                  context: Optional[Dict] = None):
        """
        Loggt einen Fehler (mit Rate-Limiting)
        
        Args:
            error_type: Fehlertyp
            error_message: Fehlermeldung
            traceback_str: Traceback (optional)
            context: Zusätzlicher Kontext (optional)
        """
        # Erstelle Hash für Fehler
        error_hash = self._get_error_hash(error_type, error_message, traceback_str)
        
        # Prüfe ob Fehler geloggt werden soll
        if not self._should_log_error(error_hash):
            logger.debug(f"Fehler {error_hash} übersprungen (Rate-Limiting)")
            return
        
        timestamp = datetime.now()
        filename = f"error-{timestamp.strftime('%Y%m%d-%H%M%S')}-{error_hash}.md"
        filepath = self.error_dir / filename
        
        # Erstelle Error-Report
        report = self._create_error_report(
            timestamp=timestamp,
            error_type=error_type,
            error_message=error_message,
            traceback_str=traceback_str,
            context=context,
            error_hash=error_hash
        )
        
        # Speichere Report
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.error(f"Error-Report erstellt: {filepath}")
            
        except Exception as e:
            logger.warning(f"Fehler beim Erstellen des Error-Reports: {e}")
    
    def _create_crash_report(self, timestamp: datetime, exc_type: str,
                            exc_message: str, exc_traceback: str,
                            context: Optional[Dict] = None) -> str:
        """Erstellt einen formatierten Crash-Report"""
        
        report = f"""# 💥 CRASH REPORT

## Zeitpunkt
**{timestamp.strftime('%d.%m.%Y %H:%M:%S')}**

## Exception
**Typ:** `{exc_type}`  
**Nachricht:** {exc_message}

## Traceback
```python
{exc_traceback}
```

## System-Information
- **Python-Version:** {sys.version}
- **Plattform:** {sys.platform}
- **Arbeitsverzeichnis:** {os.getcwd()}

"""
        
        if context:
            report += "## Kontext\n"
            for key, value in context.items():
                report += f"- **{key}:** {value}\n"
            report += "\n"
        
        report += """## Empfohlene Aktionen
1. Prüfe die Traceback-Informationen
2. Suche nach ähnlichen Crashes in diesem Ordner
3. Erstelle ein Issue im Repository mit diesem Report
4. Prüfe die Logs: `sudo journalctl -u raspi-app.service -n 100`

## Hinweis
Dieser Crash-Report wurde automatisch erstellt.
"""
        
        return report
    
    def _create_error_report(self, timestamp: datetime, error_type: str,
                            error_message: str, traceback_str: Optional[str],
                            context: Optional[Dict], error_hash: str) -> str:
        """Erstellt einen formatierten Error-Report"""
        
        error_data = self.error_cache.get(error_hash, {})
        count = error_data.get('count', 1)
        
        report = f"""# ⚠️ ERROR REPORT

## Zeitpunkt
**{timestamp.strftime('%d.%m.%Y %H:%M:%S')}**

## Fehler
**Typ:** `{error_type}`  
**Nachricht:** {error_message}  
**Hash:** `{error_hash}`  
**Vorkommen:** {count}x

"""
        
        if traceback_str:
            report += f"""## Traceback
```python
{traceback_str}
```

"""
        
        if context:
            report += "## Kontext\n"
            for key, value in context.items():
                report += f"- **{key}:** {value}\n"
            report += "\n"
        
        if count > 1:
            first_occurrence = datetime.fromtimestamp(error_data.get('first_occurrence', 0))
            report += f"""## Häufigkeit
Dieser Fehler ist bereits **{count}x** aufgetreten.  
Erstes Vorkommen: {first_occurrence.strftime('%d.%m.%Y %H:%M:%S')}

"""
        
        report += """## Hinweis
Dieser Error-Report wurde automatisch erstellt.
Ähnliche Fehler werden gruppiert um Log-Spam zu vermeiden.
"""
        
        return report
    
    def cleanup_old_logs(self, days: int = 30):
        """
        Löscht alte Log-Dateien
        
        Args:
            days: Alter in Tagen (Standard: 30)
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for log_dir in [self.crash_dir, self.error_dir]:
            for log_file in log_dir.glob('*.md'):
                try:
                    # Prüfe Änderungsdatum
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if mtime < cutoff_time:
                        log_file.unlink()
                        deleted_count += 1
                        logger.debug(f"Alte Log-Datei gelöscht: {log_file.name}")
                except Exception as e:
                    logger.warning(f"Fehler beim Löschen von {log_file}: {e}")
        
        if deleted_count > 0:
            logger.info(f"{deleted_count} alte Log-Dateien gelöscht (älter als {days} Tage)")
    
    def get_statistics(self) -> Dict:
        """
        Gibt Statistiken über Fehler zurück
        
        Returns:
            Dictionary mit Statistiken
        """
        crash_count = len(list(self.crash_dir.glob('*.md')))
        error_count = len(list(self.error_dir.glob('*.md')))
        
        # Zähle eindeutige Fehler
        unique_errors = len(self.error_cache)
        
        # Zähle Gesamt-Vorkommen
        total_occurrences = sum(
            data.get('count', 0) 
            for data in self.error_cache.values()
        )
        
        return {
            'crash_reports': crash_count,
            'error_reports': error_count,
            'unique_errors': unique_errors,
            'total_error_occurrences': total_occurrences,
            'log_directory': str(self.log_dir)
        }


# Globale Instanz
_error_logger: Optional[ErrorLogger] = None


def get_error_logger() -> ErrorLogger:
    """Gibt die globale ErrorLogger-Instanz zurück"""
    global _error_logger
    if _error_logger is None:
        _error_logger = ErrorLogger()
    return _error_logger


def setup_crash_handler():
    """
    Richtet einen globalen Exception-Handler ein
    Fängt unbehandelte Exceptions und erstellt Crash-Reports
    """
    def exception_handler(exc_type, exc_value, exc_traceback):
        """Handler für unbehandelte Exceptions"""
        # Ignoriere KeyboardInterrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Erstelle Crash-Report
        error_logger = get_error_logger()
        error_logger.log_crash(
            exception=exc_value,
            context={
                'exception_type': exc_type.__name__,
                'python_version': sys.version,
                'platform': sys.platform
            }
        )
        
        # Rufe Standard-Handler auf
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    # Setze Exception-Handler
    sys.excepthook = exception_handler
    logger.info("Globaler Crash-Handler eingerichtet")


# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

## [1.4.0] - 2025-11-26

### Hinzugefügt
- **Modus 4: Zeitsteuerung + PIR (Hybrid-Modus):**
  - Während Arbeitszeit: Dauerschleife (Bildschirm immer AN)
  - Nach Feierabend: PIR-Steuerung (Bewegungssensor)
  - Kombiniert die Vorteile von Modus 2 und Modus 1
  - Ideal für flexible Nutzung (Geschäftszeiten + Energiesparen)

### Geändert
- **GUI erweitert:**
  - Modus 4 als vierte Option hinzugefügt
  - Beschreibung für Hybrid-Modus
  - Hinweise welche Einstellungen bei welchem Modus aktiv sind

- **Slideshow-Logik:**
  - Unterstützt Hybrid-Modus mit Zeitumschaltung
  - Während Arbeitszeit: Dauerschleife-Verhalten
  - Nach Feierabend: PIR-Verhalten mit Timeout

- **Status-Anzeige:**
  - Zeigt aktuellen Modus und Zustand (Arbeitszeit/Feierabend + PIR)

### Technische Details
- Config-Version: 1.4.0
- Neuer display_mode Wert: "time_pir"
- PIR-Sensor wird in Modus 1 und 4 initialisiert
- Zeitsteuerung aktiv in Modus 2 und 4

---

## [1.3.0] - 2025-11-26

### Hinzugefügt
- **Display-Modi-System:**
  - **Modus 1: PIR-Steuerung** - Bildschirm schaltet sich bei Bewegung ein/aus
  - **Modus 2: Zeitsteuerung** - Dauerschleife während Arbeitszeit, AUS nach Feierabend
  - **Modus 3: Dauerschleife (24/7)** - Bildschirm immer an, keine Sensor-Steuerung
  
- **Modus-Validierung:**
  - Nur EIN Modus kann aktiv sein
  - Radio-Buttons in GUI für klare Auswahl
  - Automatische Config-Migration von alten Versionen

### Geändert
- **Konfiguration vereinfacht:**
  - Alte Felder `pir_enabled` und `time_control_enabled` entfernt
  - Neues Feld `display_mode` mit Werten: "pir", "time", "continuous"
  - Klarere Struktur und einfachere Bedienung

- **GUI komplett überarbeitet:**
  - Radio-Buttons statt Checkboxen für Modi
  - Beschreibungen für jeden Modus
  - Einstellungen nach Modus gruppiert
  - Bessere Übersichtlichkeit

- **Slideshow-Logik optimiert:**
  - Klare Trennung der Modi
  - Modus 2 (Zeit): Bildschirm AUS außerhalb Arbeitszeit (nicht PIR!)
  - Modus 3 (Dauerschleife): Keine Sensor-Logik, immer aktiv

### Migration
- Alte Configs werden automatisch migriert:
  - `time_control_enabled=true` → `display_mode="time"`
  - `pir_enabled=true` → `display_mode="pir"`
  - Beide false → `display_mode="continuous"`

### Technische Details
- Config-Version: 1.3.0
- Abwärtskompatibilität durch automatische Migration
- Validierung des display_mode in ConfigManager

---

## [1.2.0] - 2025-11-26

### Hinzugefügt
- **Intelligentes Error-Logging-System:**
  - Automatische Crash-Reports bei kritischen Fehlern
  - Error-Reports mit Rate-Limiting (verhindert Log-Spam)
  - Fehler-Gruppierung durch Hashing
  - Automatisches Cleanup alter Logs (>30 Tage)
  
- **Log-Viewer Tool:**
  - CLI-Tool zum Anzeigen von Logs (`./log-viewer`)
  - Befehle: `list`, `show`, `cleanup`
  - Übersichtliche Darstellung von Crash- und Error-Reports
  
- **Neue Module:**
  - `error_logger.py` - Error-Logging-System
  - `log_viewer.py` - Log-Viewer CLI

### Geändert
- **Hauptanwendung:**
  - Globaler Exception-Handler für Crash-Reports
  - Error-Logging in kritischen Funktionen
  - Fehler-Statistiken beim Beenden

- **Log-Struktur:**
  - Crashes: `~/.local/share/raspi-app/logs/crashes/`
  - Errors: `~/.local/share/raspi-app/logs/errors/`
  - Format: Markdown-Dateien mit vollständigen Details

### Technische Details
- Rate-Limiting: Erste 3 Vorkommen immer, danach alle 5 Minuten
- Fehler-Hashing: MD5-Hash der ersten 2 Traceback-Zeilen
- Automatisches Cleanup beim App-Start
- Error-Cache in JSON für persistentes Rate-Limiting

---

## [1.1.0] - 2025-11-26

### Hinzugefügt
- **Zeitsteuerung (Arbeitszeit-Modus):**
  - Neue Funktion für automatische Umschaltung zwischen Dauerschleife und PIR-Modus
  - Während Arbeitszeit: Bilder laufen durchgehend ohne PIR-Sensor
  - Außerhalb Arbeitszeit (Feierabend): PIR-Sensor-Steuerung aktiv
  - Konfigurierbare Arbeitszeiten (Start/Ende) über GUI
  - Ein/Ausschaltbar (Standard: AUS)
  
- **Update-System:**
  - Automatisches Update-Skript (`update.sh`)
  - Automatische Backup-Erstellung vor Update
  - Automatischer Rollback bei Fehlern
  - Config-Migration für neue Felder
  - Versionsverwaltung mit `VERSION`-Datei
  
- **Dokumentation:**
  - `UPDATE_GUIDE.md` - Ausführliche Update-Anleitung für Entwickler und Benutzer
  - `CHANGELOG.md` - Diese Datei
  - Detaillierte Erklärungen zum Update-Prozess

### Geändert
- **Konfiguration erweitert:**
  - Neue Felder: `time_control_enabled`, `work_start_time`, `work_end_time`, `version`
  - GUI zeigt jetzt Zeitsteuerungs-Einstellungen
  - Status-Anzeige zeigt aktuellen Modus (Arbeitszeit/Feierabend)

- **Slideshow-Logik:**
  - Unterstützt jetzt zwei Modi: Dauerschleife und PIR-gesteuert
  - Automatische Umschaltung basierend auf Uhrzeit
  - Bildschirm bleibt während Arbeitszeit immer an

- **Komponenten:**
  - Neue Klasse `TimeController` für Zeitsteuerung
  - Erweiterte `SlideshowWindow` mit Zeitsteuerungs-Integration
  - Verbesserte Status-Anzeige mit Modus-Information

### Technische Details
- Python-Module: Neues Modul `time_control.py`
- Config-Migration: Automatisch in `update.sh`
- Abwärtskompatibilität: Alte Configs funktionieren weiterhin

---

## [1.0.0] - 2025-11-25

### Hinzugefügt
- **Initiale Version der Raspberry Pi Eingangsbereich Display App**

- **PIR Motion Sensor Integration:**
  - Automatische Bewegungserkennung
  - Bildschirm schaltet sich bei Bewegung ein
  - Konfigurierbarer Timeout (Standard: 120 Sekunden)
  - Konfigurierbarer GPIO-Pin (Standard: GPIO 4)

- **Intelligente Slideshow:**
  - Automatische Bildanzeige aus konfigurierbarem Ordner
  - Unterstützte Formate: JPG, PNG, GIF, BMP, WEBP
  - Konfigurierbare Anzeigedauer (Standard: 5 Sekunden)
  - Zufällige oder sortierte Reihenfolge
  - Automatische Bildskalierung für optimale Darstellung

- **Bildschirm-Steuerung:**
  - Automatisches Ein-/Ausschalten über vcgencmd
  - HDMI-Steuerung für Energieeinsparung
  - Timeout-basiertes Ausschalten

- **Grafische Benutzeroberfläche (GUI):**
  - Tkinter-basierte Konfigurationsoberfläche
  - Alle Einstellungen über GUI konfigurierbar
  - START-Button zum Starten der Slideshow
  - Übersichtliche Gruppierung der Einstellungen

- **Konfigurationsverwaltung:**
  - JSON-basierte Konfiguration
  - Speicherung in `~/.config/raspi-app/config.json`
  - Alle Einstellungen persistent

- **Systemintegration:**
  - Automatischer Installer (`install.sh`)
  - Automatischer Deinstaller (`uninstall.sh`)
  - systemd Service-Integration
  - Autostart-Funktion (optional)
  - Automatischer Neustart nach Stromausfall

- **Tastatursteuerung:**
  - ESC-Taste: Zurück zur Konfiguration
  - SPACE-Taste: Nächstes Bild manuell

- **Hilfsskripte:**
  - `setup_autostart.sh` - Autostart einrichten
  - `create_sample_images.sh` - Testbilder erstellen

- **Dokumentation:**
  - Ausführliche README.md
  - Installationsanleitung
  - Fehlerbehebung
  - Hardware-Setup-Anleitung

### Technische Details
- Python 3.7+ kompatibel
- Tkinter für GUI
- Pillow für Bildverarbeitung
- RPi.GPIO für Sensor-Steuerung
- Vollständige Fehlerbehandlung
- Logging-System
- Virtuelle Python-Umgebung

### Konfigurierbare Optionen
- PIR Sensor: Pin, Aktivierung, Status-Anzeige
- Bildschirm: Timeout, Vollbild
- Bilder: Ordner, Anzeigedauer, Reihenfolge
- System: Autostart, Debug-Modus

---

## Versionierungsschema

- **MAJOR** (1.x.x): Große Änderungen, Breaking Changes
- **MINOR** (x.1.x): Neue Features, keine Breaking Changes  
- **PATCH** (x.x.1): Bugfixes, kleine Verbesserungen

---

## Links

- Repository: [GitHub/GitLab URL hier einfügen]
- Issues: [Issue-Tracker URL hier einfügen]
- Dokumentation: Siehe README.md und UPDATE_GUIDE.md


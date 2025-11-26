# 📦 UPDATE-ANLEITUNG für Raspberry Pi Eingangsbereich Display

Diese Datei erklärt den Update-Prozess und wie Updates strukturiert werden müssen.

## 🎯 Übersicht

Das Update-System ermöglicht es, die Anwendung zu aktualisieren ohne Konfiguration oder Daten zu verlieren.

### Was wird aktualisiert:
- ✅ Python-Code (alle Dateien in `src/app/`)
- ✅ Python-Abhängigkeiten (`requirements.txt`)
- ✅ Setup-Konfiguration (`setup.py`)
- ✅ Versionsnummer (`VERSION`)

### Was wird NICHT überschrieben:
- ✅ Benutzerkonfiguration (`~/.config/raspi-app/config.json`)
- ✅ Bilder (`~/Pictures/slideshow/`)
- ✅ Logs
- ✅ Service-Einstellungen (außer bei expliziten Service-Updates)

---

## 📋 UPDATE-PROZESS (für Entwickler/Maintainer)

### 1. Versionsnummer erhöhen

**Datei: `VERSION`**
```
1.1.0
```

**Format:** `MAJOR.MINOR.PATCH`
- **MAJOR**: Große Änderungen, Breaking Changes
- **MINOR**: Neue Features, keine Breaking Changes
- **PATCH**: Bugfixes, kleine Verbesserungen

**Auch in:** `src/app/config.py` → `AppConfig.version`

### 2. Code-Änderungen durchführen

**Dateien die aktualisiert werden können:**

```
src/app/
├── __init__.py              # Package-Info
├── main.py                  # Hauptlogik
├── config.py                # Konfiguration (WICHTIG: siehe unten)
├── gui.py                   # GUI-Fenster
├── slideshow_window.py      # Slideshow-Anzeige
├── slideshow.py             # Slideshow-Logik
├── pir_sensor.py            # PIR-Sensor-Steuerung
├── screen_control.py        # Bildschirm-Steuerung
├── time_control.py          # Zeitsteuerung
└── utils.py                 # Hilfsfunktionen
```

### 3. Neue Konfigurationsfelder hinzufügen

**WICHTIG:** Wenn neue Config-Felder hinzugefügt werden!

**Datei: `src/app/config.py`**

```python
@dataclass
class AppConfig:
    # Bestehende Felder...
    
    # NEUES FELD HINZUFÜGEN:
    new_feature_enabled: bool = False  # Standard-Wert angeben!
    new_feature_value: str = "default"
```

**Datei: `update.sh` → Funktion `migrate_config()`**

```bash
migrate_config() {
    # ...
    python3 << EOF
    # Füge neue Felder hinzu:
    if 'new_feature_enabled' not in config:
        config['new_feature_enabled'] = False
        updated = True
    
    if 'new_feature_value' not in config:
        config['new_feature_value'] = "default"
        updated = True
EOF
}
```

**REGEL:** Jedes neue Config-Feld MUSS:
1. Einen Standard-Wert in `AppConfig` haben
2. In `update.sh` → `migrate_config()` hinzugefügt werden
3. Abwärtskompatibel sein (alte Configs müssen weiter funktionieren)

### 4. Abhängigkeiten aktualisieren

**Datei: `requirements.txt`**

```txt
# Neue Pakete hinzufügen:
new-package>=1.0.0

# Versionen aktualisieren:
existing-package>=2.0.0  # von 1.0.0
```

**REGEL:** Immer `>=` verwenden, nie exakte Versionen (`==`)

### 5. GUI-Änderungen

**Datei: `src/app/gui.py`**

Wenn neue Config-Felder in der GUI angezeigt werden sollen:

```python
def _create_widgets(self):
    # ...
    
    # Neues Widget hinzufügen:
    self.vars['new_feature_enabled'] = tk.BooleanVar(value=self.config.new_feature_enabled)
    ttk.Checkbutton(main_frame, text="Neue Funktion", 
                   variable=self.vars['new_feature_enabled']).grid(...)

def _save_config(self):
    # ...
    new_config = AppConfig(
        # Bestehende Felder...
        new_feature_enabled=self.vars['new_feature_enabled'].get(),  # HINZUFÜGEN!
    )
```

### 6. Service-Updates (selten nötig)

**Nur wenn systemd Service geändert werden muss!**

**Datei: `install.sh` → Funktion `create_service()`**

Änderungen hier werden bei `sudo ./install.sh` übernommen, aber NICHT bei `sudo ./update.sh`.

Für Service-Updates manuell:
```bash
sudo systemctl stop raspi-app.service
sudo nano /etc/systemd/system/raspi-app.service
sudo systemctl daemon-reload
sudo systemctl start raspi-app.service
```

---

## 🚀 UPDATE DURCHFÜHREN (für Benutzer)

### Schritt 1: Update-Dateien herunterladen

```bash
# Git-Repository:
cd /pfad/zum/projekt
git pull

# Oder manuell:
# Lade neue Dateien herunter und ersetze alte
```

### Schritt 2: Update ausführen

```bash
chmod +x update.sh
sudo ./update.sh
```

### Schritt 3: Prüfen

```bash
# Service-Status prüfen
sudo systemctl status raspi-app.service

# Logs prüfen
sudo journalctl -u raspi-app.service -n 50

# Anwendung manuell testen
python3 -m app.main
```

### Schritt 4: Backup löschen (optional)

Wenn alles funktioniert:
```bash
# Backup-Pfad wird nach Update angezeigt
sudo rm -rf /tmp/raspi-app_backup_YYYYMMDD_HHMMSS
```

---

## 🔄 ROLLBACK (bei Problemen)

Falls das Update fehlschlägt, wird automatisch ein Rollback durchgeführt.

**Manueller Rollback:**

```bash
# Backup-Verzeichnis finden
ls -la /tmp/raspi-app_backup_*

# Neuestes Backup
BACKUP="/tmp/raspi-app_backup_YYYYMMDD_HHMMSS"

# Service stoppen
sudo systemctl stop raspi-app.service

# Alte Version wiederherstellen
sudo rm -rf /opt/raspi-app
sudo cp -r ${BACKUP}/app /opt/raspi-app

# Config wiederherstellen (optional)
rm -rf ~/.config/raspi-app
cp -r ${BACKUP}/config ~/.config/raspi-app

# Service starten
sudo systemctl start raspi-app.service
```

---

## 📝 CHANGELOG-FORMAT

**Datei: `CHANGELOG.md`** (sollte erstellt werden)

```markdown
# Changelog

## [1.1.0] - 2025-11-26

### Hinzugefügt
- Zeitsteuerung für Arbeitszeit/Feierabend-Modus
- Update-System mit automatischer Config-Migration
- Neue Config-Felder: time_control_enabled, work_start_time, work_end_time

### Geändert
- GUI erweitert um Zeitsteuerungs-Einstellungen
- Slideshow-Logik unterstützt jetzt Dauerschleife während Arbeitszeit

### Behoben
- Keine Bugfixes in dieser Version

## [1.0.0] - 2025-11-25

### Hinzugefügt
- Initiale Version
- PIR-Sensor-Steuerung
- Slideshow-Funktion
- GUI-Konfiguration
```

---

## 🧪 UPDATE TESTEN

### Vor dem Release:

1. **Backup erstellen:**
   ```bash
   sudo ./update.sh  # Erstellt automatisch Backup
   ```

2. **Konfiguration prüfen:**
   ```bash
   cat ~/.config/raspi-app/config.json
   # Prüfe ob alle neuen Felder vorhanden sind
   ```

3. **Funktionstest:**
   - Starte GUI: `python3 -m app.main`
   - Prüfe neue Features
   - Teste Slideshow
   - Teste PIR-Sensor
   - Teste Zeitsteuerung

4. **Service-Test:**
   ```bash
   sudo systemctl restart raspi-app.service
   sudo systemctl status raspi-app.service
   ```

---

## 📝 ERROR-LOGGING

### Crash-Reports erstellen

Bei kritischen Fehlern wird automatisch ein Crash-Report erstellt.

**Manuell einen Crash-Report erstellen:**

```python
from app.error_logger import get_error_logger

try:
    # Dein Code
    raise ValueError("Test-Fehler")
except Exception as e:
    error_logger = get_error_logger()
    error_logger.log_crash(e, context={'test': 'value'})
```

### Error-Reports erstellen

Für normale Fehler (mit Rate-Limiting):

```python
from app.error_logger import get_error_logger
import traceback

try:
    # Dein Code
    raise ValueError("Test-Fehler")
except Exception as e:
    error_logger = get_error_logger()
    error_logger.log_error(
        error_type=type(e).__name__,
        error_message=str(e),
        traceback_str=traceback.format_exc(),
        context={'phase': 'test'}
    )
```

### Log-Verzeichnisse

- **Crashes:** `~/.local/share/raspi-app/logs/crashes/`
- **Errors:** `~/.local/share/raspi-app/logs/errors/`

### Rate-Limiting

Das System verhindert Log-Spam durch:
1. Fehler-Hashing (ähnliche Fehler werden gruppiert)
2. Rate-Limiting (erste 3x immer, danach nur alle 5 Minuten)
3. Automatisches Cleanup (alte Logs >30 Tage)

---

## 📦 UPDATE-PAKET ERSTELLEN

### Für Distribution:

```bash
# Erstelle Update-Archiv
tar -czf raspi-app-update-v1.1.0.tar.gz \
    src/ \
    update.sh \
    requirements.txt \
    setup.py \
    VERSION \
    UPDATE_GUIDE.md \
    CHANGELOG.md

# Oder als ZIP
zip -r raspi-app-update-v1.1.0.zip \
    src/ \
    update.sh \
    requirements.txt \
    setup.py \
    VERSION \
    UPDATE_GUIDE.md \
    CHANGELOG.md
```

### Installation des Update-Pakets:

```bash
# Entpacken
tar -xzf raspi-app-update-v1.1.0.tar.gz
cd raspi-app-update-v1.1.0

# Update durchführen
chmod +x update.sh
sudo ./update.sh
```

---

## ⚠️ WICHTIGE REGELN

### DO's:
- ✅ Immer Versionsnummer erhöhen
- ✅ Standard-Werte für neue Config-Felder angeben
- ✅ Config-Migration in `update.sh` hinzufügen
- ✅ Abwärtskompatibilität beachten
- ✅ Changelog pflegen
- ✅ Vor Release testen

### DON'Ts:
- ❌ Keine Breaking Changes ohne MAJOR-Version-Erhöhung
- ❌ Keine Config-Felder ohne Standard-Werte
- ❌ Keine Änderungen an Benutzerdaten (Bilder, Logs)
- ❌ Kein Update ohne Backup-Mechanismus
- ❌ Keine exakten Versionen in requirements.txt (`==`)

---

## 🔍 DEBUGGING

### Update-Logs prüfen:

```bash
# Update-Skript mit Debug-Ausgabe
bash -x update.sh
```

### Config-Migration testen:

```python
# Python-Shell
python3
>>> from app.config import ConfigManager
>>> cm = ConfigManager()
>>> config = cm.get()
>>> print(config)
>>> # Prüfe alle Felder
```

---

## 📞 SUPPORT

Bei Problemen:
1. Prüfe Logs: `sudo journalctl -u raspi-app.service -n 100`
2. Prüfe Config: `cat ~/.config/raspi-app/config.json`
3. Teste manuell: `python3 -m app.main`
4. Rollback durchführen (siehe oben)

---

## 🎓 ZUSAMMENFASSUNG FÜR KI/ENTWICKLER

**Wenn du diese Datei liest, um ein Update zu erstellen:**

1. **Versionsnummer erhöhen:** `VERSION` + `config.py`
2. **Code ändern:** Beliebige Dateien in `src/app/`
3. **Neue Config-Felder:** In `config.py` UND `update.sh` hinzufügen
4. **GUI aktualisieren:** Wenn neue Felder sichtbar sein sollen
5. **Dependencies:** `requirements.txt` aktualisieren
6. **Testen:** Vor Release ausgiebig testen
7. **Dokumentieren:** Diese Datei und Changelog aktualisieren

**Update-Befehl für Benutzer:** `sudo ./update.sh`

**Rollback:** Automatisch bei Fehler, oder manuell aus `/tmp/raspi-app_backup_*/`

**Config-Migration:** Automatisch in `update.sh` → `migrate_config()`


# Raspberry Pi Eingangsbereich Display

Eine intelligente Slideshow-Anwendung für den Raspberry Pi mit PIR-Bewegungssensor-Steuerung für den Eingangsbereich.

## 📋 Übersicht

Diese App bietet ein vollständiges Display-System für Eingangsbereiche:

- ✅ **PIR Bewegungssensor-Steuerung** - Bildschirm schaltet sich automatisch bei Bewegung ein/aus
- ✅ **Intelligente Slideshow** - Zeigt Bilder aus einem konfigurierbaren Ordner
- ✅ **GUI-Konfiguration** - Einfache Einstellungen über grafische Oberfläche
- ✅ **Automatischer Bildschirm-Timeout** - Energiesparend durch automatisches Ausschalten
- ✅ **Zeitsteuerung** - Arbeitszeit-Modus: Dauerschleife während Arbeitszeit, PIR-Modus nach Feierabend
- ✅ **Autostart** - Startet automatisch nach Stromausfall/Neustart
- ✅ **ESC-Taste** - Jederzeit zurück zur Konfiguration
- ✅ **Update-System** - Einfache Updates ohne Datenverlust
- ✅ **Vollbild-Modus** - Professionelle Präsentation
- ✅ **Flexible Bildanzeige** - Zufällig oder sortiert, konfigurierbare Anzeigedauer

## 🚀 Schnellstart

### Voraussetzungen

- Raspberry Pi (alle Modelle, getestet mit Pi 3/4)
- Raspbian/Raspberry Pi OS mit Desktop
- Python 3.7 oder höher
- PIR Motion Sensor HAT (optional, kann auch ohne betrieben werden)
- HDMI-Monitor
- Root-Zugriff (sudo)

### Hardware-Setup

1. **PIR Sensor anschließen:**
   - Standard-Pin: GPIO 4 (BCM)
   - VCC → 5V
   - GND → GND
   - OUT → GPIO 4

2. **Monitor per HDMI anschließen**

### Software-Installation

1. Repository klonen oder Dateien auf den Raspberry Pi kopieren:

```bash
git clone <repository-url>
cd raspberry-pi-app
```

2. Installer ausführbar machen und starten:

```bash
chmod +x install.sh
chmod +x create_sample_images.sh
chmod +x setup_autostart.sh
sudo ./install.sh
```

3. (Optional) Beispielbilder erstellen zum Testen:

```bash
./create_sample_images.sh
```

4. Eigene Bilder hinzufügen:

```bash
# Standard-Ordner: ~/Pictures/slideshow
cp /pfad/zu/deinen/bildern/* ~/Pictures/slideshow/
```

5. Anwendung starten:

```bash
# Manuell starten
python3 -m app.main

# Oder als Service
sudo systemctl start raspi-app.service
```

### Update durchführen

```bash
# Update-Skript ausführbar machen
chmod +x update.sh

# Update durchführen
sudo ./update.sh
```

**Hinweis:** Lese `UPDATE_GUIDE.md` für Details zum Update-Prozess.

### Deinstallation

```bash
sudo ./uninstall.sh
```

## 📁 Projektstruktur

```
raspberry-pi-app/
├── src/app/
│   ├── __init__.py              # Package-Initialisierung
│   ├── main.py                  # Hauptanwendung
│   ├── config.py                # Konfigurationsverwaltung
│   ├── gui.py                   # Konfigurations-GUI
│   ├── slideshow_window.py      # Slideshow-Fenster
│   ├── slideshow.py             # Slideshow-Logik
│   ├── pir_sensor.py            # PIR Sensor-Steuerung
│   ├── screen_control.py        # Bildschirm Ein/Aus
│   └── utils.py                 # Hilfsfunktionen
├── install.sh                   # Installer-Skript
├── uninstall.sh                 # Deinstaller-Skript
├── setup_autostart.sh           # Autostart-Setup
├── create_sample_images.sh      # Beispielbilder erstellen
├── requirements.txt             # Python-Abhängigkeiten
├── setup.py                     # Setup-Konfiguration
├── .gitignore                   # Git-Ignore-Datei
└── README.md                    # Diese Datei
```

## 🔧 Verwendung

### Erste Schritte

1. **Anwendung starten:**
   - Nach Installation öffnet sich automatisch das Konfigurationsfenster
   - Oder manuell starten: `python3 -m app.main`

2. **Konfiguration anpassen:**
   
   **Display-Modus wählen (nur EINER aktiv):**
   
   - **Modus 1: PIR-Steuerung** *(Standard)*
     - Bildschirm AN bei Bewegung
     - Bildschirm AUS nach Timeout (keine Bewegung)
     - GPIO-Pin: Standard GPIO 4
     - Timeout: Standard 120 Sekunden
     
   - **Modus 2: Zeitsteuerung (Arbeitszeit)**
     - Während Arbeitszeit: Dauerschleife (immer AN)
     - Außerhalb Arbeitszeit: Bildschirm AUS
     - Arbeitsbeginn: z.B. 08:00
     - Feierabend: z.B. 17:00
     
   - **Modus 3: Dauerschleife (24/7)**
     - Bildschirm IMMER AN
     - Keine Sensor-Steuerung
     - Ideal für permanente Anzeige
     
   - **Modus 4: Zeitsteuerung + PIR (Hybrid)** ⭐ *NEU*
     - Während Arbeitszeit: Dauerschleife (immer AN)
     - Nach Feierabend: PIR-Steuerung (Bewegungssensor)
     - Kombiniert Modus 1 und 2
     - Ideal für flexible Nutzung
   
   **Weitere Einstellungen:**
   - **Bildordner:** Pfad zu deinen Bildern auswählen
   - **Anzeigedauer:** Wie lange jedes Bild angezeigt wird (Standard: 5 Sekunden)
   - **Reihenfolge:** Zufällig oder sortiert
   - **Autostart:** Automatisch beim Booten starten

3. **START klicken:**
   - Slideshow startet im Vollbildmodus
   - Verhalten je nach gewähltem Modus:
     - **Modus 1 (PIR):** Bildschirm bei Bewegung AN, nach Timeout AUS
     - **Modus 2 (Zeit):** Während Arbeitszeit AN, nach Feierabend AUS
     - **Modus 3 (24/7):** Immer AN
     - **Modus 4 (Zeit+PIR):** Arbeitszeit AN, Feierabend PIR-gesteuert

4. **ESC-Taste drücken:**
   - Zurück zur Konfiguration
   - Einstellungen anpassen
   - Neue Bilder hinzufügen

### Tastenkombinationen

- **ESC** - Zurück zur Konfiguration
- **SPACE** - Nächstes Bild (während Slideshow)

### Service-Verwaltung

```bash
# Service starten
sudo systemctl start raspi-app.service

# Service stoppen
sudo systemctl stop raspi-app.service

# Service-Status prüfen
sudo systemctl status raspi-app.service

# Autostart aktivieren
sudo systemctl enable raspi-app.service

# Autostart deaktivieren
sudo systemctl disable raspi-app.service

# Logs anzeigen
sudo journalctl -u raspi-app.service -f
```

## ⚙️ Konfiguration

Die Konfiguration wird über die GUI verwaltet und in `~/.config/raspi-app/config.json` gespeichert.

### Konfigurationsoptionen

| Option | Beschreibung | Standard |
|--------|--------------|----------|
| **Display-Modus** | *(nur EINER aktiv)* | |
| Modus 1: PIR | Bewegungssensor-Steuerung | ✅ Aktiv |
| Modus 2: Zeit | Arbeitszeit-Steuerung | Inaktiv |
| Modus 3: 24/7 | Dauerschleife | Inaktiv |
| Modus 4: Zeit+PIR | Hybrid-Modus | Inaktiv |
| **PIR-Einstellungen** | *(bei Modus 1 und 4)* | |
| GPIO Pin | Pin-Nummer (BCM) | 4 |
| Timeout | Sekunden bis Ausschalten | 120 |
| **Zeit-Einstellungen** | *(bei Modus 2 und 4)* | |
| Arbeitsbeginn | Start der Dauerschleife | 08:00 |
| Feierabend | Ende / PIR-Start (Modus 4) | 17:00 |
| **Allgemein** | | |
| Vollbild | Vollbildmodus | Ja |
| Status anzeigen | Info-Anzeige in Slideshow | Ja |
| **Bilder** | | |
| Ordner | Pfad zu Bildern | ~/Pictures/slideshow |
| Anzeigedauer | Sekunden pro Bild | 5 |
| Zufällige Reihenfolge | Shuffle | Nein |
| **System** | | |
| Autostart | Beim Booten starten | Ja |
| Debug-Modus | Erweiterte Logs | Nein |

### Manuelle Konfiguration

```bash
# Konfigurationsdatei bearbeiten
nano ~/.config/raspi-app/config.json
```

## 📝 Logs

Log-Dateien befinden sich in:
- `/var/log/raspi-app.log` - Anwendungs-Logs
- `journalctl -u raspi-app.service` - systemd Service-Logs

## 🔌 GPIO-Pins & Hardware

### PIR Motion Sensor HAT

**Standard-Verkabelung:**
- **VCC** → 5V (Pin 2 oder 4)
- **GND** → GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)
- **OUT** → GPIO 4 (Pin 7) - konfigurierbar in GUI

**Unterstützte Sensoren:**
- HC-SR501 PIR Motion Sensor
- PIR Motion Sensor HAT
- Andere PIR-Sensoren mit digitalem Ausgang

### Pin-Belegung (BCM-Nummerierung)

```
GPIO 4 (Standard) - PIR Sensor OUT
```

**Hinweis:** Die Pin-Nummer kann in der GUI-Konfiguration geändert werden.

## 🛠️ Entwicklung & Anpassung

### Lokale Entwicklung

```bash
# Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# App im Development-Modus installieren
pip install -e .

# App ausführen
python -m app.main
```

### Eigene Anpassungen

**Bildübergänge hinzufügen:**
- Bearbeite `src/app/slideshow_window.py`
- Füge Fade-Effekte oder andere Übergänge hinzu

**Zusätzliche Sensoren:**
- Erstelle neue Sensor-Klasse nach Vorbild von `pir_sensor.py`
- Integriere in `main.py`

**Andere Bildschirmsteuerung:**
- Passe `screen_control.py` an
- Unterstütze andere Display-Typen

**GUI erweitern:**
- Bearbeite `gui.py` für neue Einstellungen
- Füge neue Konfigurationsoptionen in `config.py` hinzu

### Bilder dynamisch laden

```bash
# Bilder von Netzwerk-Share mounten
sudo mount -t cifs //server/share ~/Pictures/slideshow -o user=username

# Oder Symlink erstellen
ln -s /pfad/zu/netzwerk/ordner ~/Pictures/slideshow
```

## 📦 Abhängigkeiten

### Python-Pakete
- **RPi.GPIO** - GPIO-Zugriff für PIR Sensor
- **gpiozero** - High-Level GPIO-Interface
- **Pillow** - Bildverarbeitung und -anzeige
- **tkinter** - GUI-Framework
- **pyyaml** - Konfigurationsverwaltung

### System-Pakete
- **python3-tk** - Tkinter für Python 3
- **python3-pil** - PIL/Pillow für Python 3
- **libjpeg-dev** - JPEG-Unterstützung
- **libraspberrypi-bin** - vcgencmd für Bildschirmsteuerung

## 📊 Fehlerprotokollierung

Die App verfügt über ein intelligentes Error-Logging-System:

### Crash-Reports
Bei kritischen Fehlern (Crashes) wird automatisch ein detaillierter Report erstellt:
- **Speicherort:** `~/.local/share/raspi-app/logs/crashes/`
- **Format:** `crash-YYYYMMDD-HHMMSS.md`
- **Inhalt:** Vollständiger Traceback, System-Info, Kontext

### Error-Reports
Normale Fehler werden mit intelligentem Rate-Limiting geloggt:
- **Speicherort:** `~/.local/share/raspi-app/logs/errors/`
- **Format:** `error-YYYYMMDD-HHMMSS-HASH.md`
- **Rate-Limiting:** Verhindert Log-Spam
  - Erste 3 Vorkommen: Immer loggen
  - Danach: Nur alle 5 Minuten
  - Ähnliche Fehler werden gruppiert

### Log-Viewer

```bash
# Logs anzeigen
./log-viewer list

# Bestimmten Log öffnen
./log-viewer show crash-20251126-143022.md

# Alte Logs löschen (älter als 30 Tage)
./log-viewer cleanup --days 30
```

### Automatisches Cleanup
- Alte Logs (>30 Tage) werden beim App-Start automatisch gelöscht
- Manuelles Cleanup mit `log-viewer cleanup`

## 🐛 Fehlerbehebung

### GUI startet nicht

```bash
# Prüfe ob X11 läuft
echo $DISPLAY

# Sollte :0 oder :0.0 ausgeben
# Falls leer, setze:
export DISPLAY=:0

# Tkinter testen
python3 -c "import tkinter"
```

### Bildschirm schaltet sich nicht aus

```bash
# Teste vcgencmd
vcgencmd display_power 0  # Aus
vcgencmd display_power 1  # Ein

# Falls Fehler, installiere:
sudo apt-get install libraspberrypi-bin
```

### PIR Sensor reagiert nicht

**Automatische Erkennung:**
Die App erkennt automatisch ob ein PIR-Sensor verfügbar ist. Wenn kein Sensor erkannt wird:
- Modi 1 (PIR) und 4 (Zeit+PIR) werden automatisch deaktiviert
- Nur Modi 2 (Zeit) und 3 (24/7) sind wählbar
- Orange Warnung in der GUI: "⚠️ PIR-Sensor nicht erkannt"

**Manueller Test:**
```bash
# Teste GPIO
python3 << EOF
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)
print("GPIO 4 Status:", GPIO.input(4))
GPIO.cleanup()
EOF

# Prüfe Verkabelung
# Teste mit anderem Pin in GUI
```

**Wenn Sensor nicht erkannt wird:**
1. Prüfe Verkabelung (VCC, GND, OUT)
2. Prüfe ob Pin korrekt ist (Standard: GPIO 4)
3. Verwende Modus 2 (Zeit) oder 3 (24/7) als Alternative

### Bilder werden nicht angezeigt

```bash
# Prüfe Bildordner
ls -la ~/Pictures/slideshow/

# Unterstützte Formate: JPG, PNG, GIF, BMP, WEBP
# Prüfe Berechtigungen
chmod 644 ~/Pictures/slideshow/*
```

### Service startet nicht

```bash
# Status prüfen
sudo systemctl status raspi-app.service

# Detaillierte Logs
sudo journalctl -u raspi-app.service -n 50

# Service neu starten
sudo systemctl restart raspi-app.service
```

### Autostart funktioniert nicht

```bash
# Prüfe ob Service aktiviert ist
sudo systemctl is-enabled raspi-app.service

# Aktivieren
sudo systemctl enable raspi-app.service

# Oder verwende Setup-Skript
./setup_autostart.sh
```

### Crash-Reports und Error-Logs prüfen

```bash
# Alle Logs anzeigen
./log-viewer list

# Nur Crash-Reports
./log-viewer list --type crash

# Nur Error-Reports
./log-viewer list --type error

# Bestimmten Log anzeigen
./log-viewer show crash-20251126-143022.md

# Alte Logs löschen (älter als 30 Tage)
./log-viewer cleanup --days 30

# Zeige was gelöscht würde (ohne zu löschen)
./log-viewer cleanup --dry-run
```

**Log-Verzeichnis:** `~/.local/share/raspi-app/logs/`
- `crashes/` - Crash-Reports (kritische Fehler)
- `errors/` - Error-Reports (normale Fehler mit Rate-Limiting)

## 📄 Lizenz

MIT License - siehe LICENSE-Datei für Details

## 👤 Autor

Leon Haas - haas-leon-2002@gmx.de

## 🤝 Beitragen

Contributions, Issues und Feature-Requests sind willkommen!

## 🔄 Updates

### Update durchführen

```bash
# Update-Dateien herunterladen (Git)
git pull

# Update ausführen
chmod +x update.sh
sudo ./update.sh
```

### Was wird aktualisiert:
- ✅ Python-Code
- ✅ Abhängigkeiten
- ✅ Konfiguration (neue Felder werden automatisch hinzugefügt)

### Was bleibt erhalten:
- ✅ Deine Einstellungen
- ✅ Deine Bilder
- ✅ Logs

**Wichtig:** Vor jedem Update wird automatisch ein Backup erstellt!

Siehe `UPDATE_GUIDE.md` für Details.

---

## ⭐ Support

Bei Fragen oder Problemen erstelle bitte ein Issue im Repository.

### Wichtige Dateien:
- `README.md` - Diese Datei (Hauptdokumentation)
- `UPDATE_GUIDE.md` - Update-Anleitung für Entwickler und Benutzer
- `CHANGELOG.md` - Liste aller Änderungen pro Version


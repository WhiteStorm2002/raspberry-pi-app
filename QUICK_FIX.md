# 🚨 QUICK FIX - START-Button Problem

## Problem
START-Button zeigt "Konfiguration gespeichert" Messagebox und App schließt sich.

## Ursache
Die alte Version von `gui.py` läuft noch auf dem Raspberry Pi.

## ✅ Lösung (auf dem Raspberry Pi ausführen):

### Schritt 1: Stoppe die App
```bash
sudo systemctl stop raspi-app.service
```

### Schritt 2: Hole die neueste Version
```bash
cd ~/raspberry-pi-app
git pull origin main
```

### Schritt 3: Kopiere die neue gui.py
```bash
sudo cp src/app/gui.py /opt/raspi-app/app/gui.py
sudo cp src/app/main.py /opt/raspi-app/app/main.py
```

### Schritt 4: Teste direkt
```bash
cd /opt/raspi-app
./venv/bin/python3 -m app.main
```

### Schritt 5: Teste den START-Button
1. GUI sollte sich öffnen
2. Klicke auf START
3. **KEINE** "Erfolg"-Messagebox sollte erscheinen
4. Slideshow sollte starten

---

## 🐛 Wenn es immer noch nicht funktioniert:

### Debug-Test (auf dem Raspberry Pi):
```bash
cd ~/raspberry-pi-app
python3 debug_start.py
```

Das zeigt dir genau was beim START-Button passiert.

---

## 📋 Checkliste:

- [ ] App gestoppt
- [ ] Neueste Dateien von GitHub geholt
- [ ] gui.py und main.py kopiert
- [ ] Mit ./run.sh getestet
- [ ] START-Button funktioniert ohne Messagebox
- [ ] Slideshow startet

---

## 💡 Alternative: Komplette Neuinstallation

Falls nichts hilft:

```bash
# 1. Deinstallieren
sudo ./uninstall.sh

# 2. Neu installieren
sudo ./install.sh

# 3. Testen
./run.sh
```

---

## 🔍 Was der START-Button jetzt macht:

```python
def _start_slideshow(self):
    # 1. Validiere Modus
    # 2. Erstelle Config
    # 3. Speichere Config (OHNE messagebox.showinfo!)
    # 4. Verstecke Fenster
    # 5. Rufe Callback auf → Startet Slideshow
    # KEINE Messagebox! ✅
```

## 🔍 Was der SPEICHERN-Button macht:

```python
def _save_config(self):
    # 1. Validiere Modus
    # 2. Erstelle Config
    # 3. Speichere Config
    # 4. Zeige messagebox.showinfo("Erfolg", ...) ✅
    # 5. Bleibt in der Config
```

---

## 📞 Wenn es immer noch nicht geht:

Führe aus und schicke mir die Ausgabe:
```bash
cd /opt/raspi-app
./venv/bin/python3 -m app.main 2>&1 | tee app_debug.log
```

Dann können wir sehen was genau passiert.


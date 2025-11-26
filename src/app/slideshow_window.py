#!/usr/bin/env python3
"""
Slideshow-Fenster für die Bildanzeige
"""

import tkinter as tk
from tkinter import ttk
import logging
import time
from typing import Optional, Callable
from pathlib import Path

from .slideshow import Slideshow
from .pir_sensor import PIRSensor
from .screen_control import ScreenController
from .time_control import TimeController
from .config import AppConfig

logger = logging.getLogger(__name__)


class SlideshowWindow:
    """Vollbild-Slideshow-Fenster"""
    
    def __init__(self, config: AppConfig, on_exit_callback: Optional[Callable] = None):
        """
        Initialisiert das Slideshow-Fenster
        
        Args:
            config: App-Konfiguration
            on_exit_callback: Callback wenn ESC gedrückt wird
        """
        self.config = config
        self.on_exit_callback = on_exit_callback
        
        # Fenster erstellen
        self.root = tk.Toplevel()
        self.root.title("Slideshow")
        
        # Vollbild-Konfiguration (wie PowerPoint)
        if config.fullscreen:
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-topmost', True)  # Immer im Vordergrund
            self.root.overrideredirect(True)  # Entfernt Fensterrahmen komplett
        else:
            self.root.geometry("1920x1080")
        
        # Mauszeiger verstecken (wenn aktiviert)
        cursor_style = 'none' if getattr(config, 'hide_cursor', True) else ''
        self.root.configure(bg='black', cursor=cursor_style)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Komponenten
        self.slideshow = Slideshow(config.image_folder, config.random_order)
        self.screen_controller = ScreenController()
        self.time_controller = TimeController(
            enabled=(config.display_mode in ["time", "time_pir"]),
            work_start=config.work_start_time,
            work_end=config.work_end_time
        )
        self.pir_sensor: Optional[PIRSensor] = None
        
        # Status
        self.running = False
        self.screen_active = True
        self.last_motion_time = time.time()
        self.current_image_time = 0
        self.current_mode = ""  # Arbeitszeit oder Feierabend
        self.display_mode = config.display_mode  # "pir", "time", "continuous", "time_pir"
        
        # GUI-Elemente
        self._create_widgets()
        
        # Tastenbindungen
        self.root.bind('<Escape>', self._on_escape)
        self.root.bind('<space>', lambda e: self._next_image())
        
        # PIR Sensor initialisieren (im PIR-Modus und Zeit+PIR-Modus)
        if config.display_mode in ["pir", "time_pir"]:
            self._init_pir_sensor()
        
        logger.info("Slideshow-Fenster erstellt")
    
    def _create_widgets(self):
        """Erstellt die GUI-Elemente"""
        # Hauptframe
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Bild-Label (zentriert)
        self.image_label = tk.Label(self.main_frame, bg='black')
        self.image_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Status-Label (oben links)
        if self.config.show_sensor_status:
            self.status_label = tk.Label(
                self.main_frame,
                text="",
                fg='white',
                bg='black',
                font=('Arial', 12),
                anchor='w'
            )
            self.status_label.place(x=10, y=10)
        else:
            self.status_label = None
        
        # Info-Label (unten) - nur im Debug-Modus
        if self.config.debug_mode:
            self.info_label = tk.Label(
                self.main_frame,
                text="ESC = Konfiguration | SPACE = Nächstes Bild",
                fg='gray',
                bg='black',
                font=('Arial', 10)
            )
            self.info_label.place(relx=0.5, rely=0.98, anchor=tk.S)
        else:
            self.info_label = None
    
    def _init_pir_sensor(self):
        """Initialisiert den PIR Sensor"""
        try:
            self.pir_sensor = PIRSensor(
                pin=self.config.pir_pin,
                callback=self._on_motion_detected
            )
            self.pir_sensor.start_monitoring()
            logger.info("PIR Sensor gestartet")
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren des PIR Sensors: {e}")
    
    def _on_motion_detected(self, motion: bool):
        """
        Callback für Bewegungserkennung
        
        Args:
            motion: True wenn Bewegung erkannt, False wenn keine Bewegung
        """
        if motion:
            logger.info("Bewegung erkannt - Bildschirm einschalten")
            self.last_motion_time = time.time()
            
            if not self.screen_active:
                self.screen_controller.turn_on()
                self.screen_active = True
                self._update_status("Bewegung erkannt - Bildschirm AN")
        else:
            logger.info("Keine Bewegung mehr")
            self._update_status("Keine Bewegung")
    
    def _update_status(self, text: str):
        """Aktualisiert den Status-Text"""
        if self.status_label:
            # Füge Modus-Info hinzu
            mode_descriptions = {
                "pir": "MODUS: PIR-Steuerung (Bewegungssensor)",
                "time": self.time_controller.get_mode_description(),
                "continuous": "MODUS: Dauerschleife (24/7 aktiv)",
                "time_pir": self.time_controller.get_mode_description() + " + PIR"
            }
            mode_info = mode_descriptions.get(self.display_mode, "MODUS: Unbekannt")
            full_text = f"{mode_info}\n{text}"
            self.status_label.config(text=full_text)
    
    def _next_image(self):
        """Zeigt das nächste Bild an"""
        try:
            # Hole nächstes Bild
            image_path = self.slideshow.get_next_image()
            
            if not image_path:
                self._update_status("Keine Bilder gefunden!")
                logger.warning("Keine Bilder im Ordner")
                return
            
            # Lade und zeige Bild
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            if width <= 1 or height <= 1:
                # Fenster noch nicht initialisiert
                width, height = 1920, 1080
            
            photo = self.slideshow.load_image_for_display(image_path, width, height)
            
            if photo:
                self.image_label.config(image=photo)
                self.image_label.image = photo  # Referenz behalten!
                
                # Status aktualisieren
                count = self.slideshow.get_image_count()
                index = self.slideshow.get_current_index()
                self._update_status(f"Bild {index}/{count} - {image_path.name}")
                
                self.current_image_time = time.time()
                logger.debug(f"Zeige Bild: {image_path.name}")
            
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen des Bildes: {e}")
    
    def _check_screen_timeout(self):
        """Prüft ob Bildschirm-Timeout erreicht ist"""
        
        # === MODUS 1: PIR-Steuerung ===
        if self.display_mode == "pir":
            current_time = time.time()
            time_since_motion = current_time - self.last_motion_time
            
            if time_since_motion > self.config.screen_timeout and self.screen_active:
                logger.info("PIR-Modus: Bildschirm-Timeout erreicht - Bildschirm ausschalten")
                self.screen_controller.turn_off()
                self.screen_active = False
                self._update_status("Bildschirm AUS (Timeout)")
        
        # === MODUS 2: Zeitsteuerung ===
        elif self.display_mode == "time":
            is_work_time = self.time_controller.is_work_time()
            
            if is_work_time:
                # Während Arbeitszeit: Bildschirm immer an
                if not self.screen_active:
                    logger.info("Arbeitszeit - Bildschirm einschalten")
                    self.screen_controller.turn_on()
                    self.screen_active = True
                    self._update_status("Arbeitszeit - Dauerschleife aktiv")
            else:
                # Außerhalb Arbeitszeit: Bildschirm aus
                if self.screen_active:
                    logger.info("Feierabend - Bildschirm ausschalten")
                    self.screen_controller.turn_off()
                    self.screen_active = False
                    self._update_status("Feierabend - Bildschirm AUS")
        
        # === MODUS 3: Dauerschleife (24/7) ===
        elif self.display_mode == "continuous":
            # Bildschirm immer an
            if not self.screen_active:
                logger.info("Dauerschleife-Modus - Bildschirm einschalten")
                self.screen_controller.turn_on()
                self.screen_active = True
                self._update_status("Dauerschleife aktiv (24/7)")
        
        # === MODUS 4: Zeitsteuerung + PIR ===
        elif self.display_mode == "time_pir":
            is_work_time = self.time_controller.is_work_time()
            
            if is_work_time:
                # Während Arbeitszeit: Dauerschleife (wie Modus 2)
                if not self.screen_active:
                    logger.info("Zeit+PIR: Arbeitszeit - Bildschirm einschalten")
                    self.screen_controller.turn_on()
                    self.screen_active = True
                    self._update_status("Arbeitszeit - Dauerschleife aktiv")
            else:
                # Außerhalb Arbeitszeit: PIR-Steuerung (wie Modus 1)
                current_time = time.time()
                time_since_motion = current_time - self.last_motion_time
                
                if time_since_motion > self.config.screen_timeout and self.screen_active:
                    logger.info("Zeit+PIR: Feierabend - PIR-Timeout erreicht")
                    self.screen_controller.turn_off()
                    self.screen_active = False
                    self._update_status("Feierabend - PIR aktiv (Bildschirm AUS)")
    
    def _check_image_change(self):
        """Prüft ob Bild gewechselt werden soll"""
        
        # Nur Bilder wechseln wenn Bildschirm aktiv ist
        # AUSNAHME: Im Zeit-Modus während Arbeitszeit oder Dauerschleife-Modus
        should_change = False
        
        if self.display_mode == "pir":
            # PIR-Modus: Nur bei aktivem Bildschirm
            should_change = self.screen_active
        
        elif self.display_mode == "time":
            # Zeit-Modus: Nur während Arbeitszeit
            should_change = self.time_controller.is_work_time()
        
        elif self.display_mode == "continuous":
            # Dauerschleife: Immer
            should_change = True
        
        elif self.display_mode == "time_pir":
            # Zeit+PIR-Modus: Während Arbeitszeit immer, sonst nur bei aktivem Bildschirm
            is_work_time = self.time_controller.is_work_time()
            if is_work_time:
                should_change = True  # Arbeitszeit: Immer
            else:
                should_change = self.screen_active  # Feierabend: Nur wenn Bildschirm an
        
        if not should_change:
            return
        
        current_time = time.time()
        time_since_image = current_time - self.current_image_time
        
        if time_since_image >= self.config.image_duration:
            self._next_image()
    
    def _update_loop(self):
        """Hauptupdate-Schleife"""
        if not self.running:
            return
        
        try:
            self._check_screen_timeout()
            self._check_image_change()
            
            # Nächstes Update planen
            self.root.after(100, self._update_loop)
            
        except Exception as e:
            logger.error(f"Fehler in Update-Schleife: {e}")
    
    def _on_escape(self, event=None):
        """ESC-Taste gedrückt - zurück zur Konfiguration"""
        logger.info("ESC gedrückt - zurück zur Konfiguration")
        
        # Mauszeiger wieder anzeigen
        self.root.configure(cursor='')
        
        self.stop()
        
        if self.on_exit_callback:
            self.on_exit_callback()
    
    def _on_closing(self):
        """Fenster wird geschlossen"""
        self.stop()
    
    def start(self):
        """Startet die Slideshow"""
        if self.running:
            return
        
        self.running = True
        self.screen_active = True
        self.last_motion_time = time.time()
        self.current_image_time = 0
        
        # Bildschirm einschalten
        self.screen_controller.turn_on()
        
        # Erstes Bild anzeigen
        self.root.after(100, self._next_image)
        
        # Update-Schleife starten
        self.root.after(200, self._update_loop)
        
        logger.info("Slideshow gestartet")
    
    def stop(self):
        """Stoppt die Slideshow"""
        if not self.running:
            return
        
        self.running = False
        
        # PIR Sensor stoppen
        if self.pir_sensor:
            self.pir_sensor.cleanup()
        
        # Bildschirm einschalten (für Konfiguration)
        self.screen_controller.turn_on()
        
        # Fenster verstecken
        self.root.withdraw()
        
        logger.info("Slideshow gestoppt")
    
    def show(self):
        """Zeigt das Slideshow-Fenster"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        
        # Verstecke Mauszeiger (wenn aktiviert)
        if getattr(self.config, 'hide_cursor', True):
            self.root.configure(cursor='none')
        
        # Stelle sicher dass Vollbild aktiv ist
        if self.config.fullscreen:
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-topmost', True)
            self.root.overrideredirect(True)  # Keine Ränder!
    
    def hide(self):
        """Versteckt das Slideshow-Fenster"""
        self.root.withdraw()


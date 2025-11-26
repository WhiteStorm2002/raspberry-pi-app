#!/usr/bin/env python3
"""
GUI für die Eingangsbereich App
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from pathlib import Path
from typing import Optional, Callable

from .config import ConfigManager, AppConfig
from .sensor_detector import get_sensor_detector

logger = logging.getLogger(__name__)


class ConfigGUI:
    """Konfigurationsfenster"""
    
    def __init__(self, config_manager: ConfigManager, on_start_callback: Optional[Callable] = None):
        """
        Initialisiert das GUI
        
        Args:
            config_manager: ConfigManager-Instanz
            on_start_callback: Callback wenn Start-Button geklickt wird
        """
        self.config_manager = config_manager
        self.config = config_manager.get()
        self.on_start_callback = on_start_callback
        
        # Sensor-Detektor
        self.sensor_detector = get_sensor_detector()
        self.available_modes = self.sensor_detector.get_available_modes()
        self.pir_available = self.sensor_detector.is_pir_available()
        
        # Hauptfenster
        self.root = tk.Tk()
        self.root.title("Eingangsbereich Display - Konfiguration")
        self.root.geometry("850x700")
        self.root.resizable(True, True)
        
        # Minimale Fenstergröße
        self.root.minsize(800, 600)
        
        # Variablen
        self.vars = {}
        
        self._create_widgets()
        self._load_values()
        
        logger.info(f"Konfigurations-GUI erstellt (PIR verfügbar: {self.pir_available})")
    
    def _create_widgets(self):
        """Erstellt alle GUI-Elemente"""
        
        # Hauptcontainer mit Canvas und Scrollbar
        container = ttk.Frame(self.root)
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        
        # Canvas für Scrolling
        canvas = tk.Canvas(container, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Konfiguriere Canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame innerhalb Canvas
        main_frame = ttk.Frame(canvas, padding="10")
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # Update scroll region wenn sich Größe ändert
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Passe Canvas-Breite an
            canvas_width = event.width if event else canvas.winfo_width()
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        main_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_scroll_region)
        
        # Mausrad-Scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def on_mousewheel_linux(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
        
        # Bind Mausrad (Windows/Mac)
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        # Bind Mausrad (Linux)
        canvas.bind_all("<Button-4>", on_mousewheel_linux)
        canvas.bind_all("<Button-5>", on_mousewheel_linux)
        
        # Titel
        title = ttk.Label(main_frame, text="Eingangsbereich Display Konfiguration", 
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        row = 1
        
        # === Display-Modus Auswahl ===
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, 
                                                            sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        ttk.Label(main_frame, text="Display-Modus", 
                 font=('Arial', 14, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1
        
        ttk.Label(main_frame, text="Wähle EINEN Modus (es muss immer einer aktiv sein):", 
                 foreground='blue', font=('Arial', 9)).grid(row=row, column=0, columnspan=2, 
                                                             sticky=tk.W, pady=(0, 5))
        row += 1
        
        # Sensor-Status anzeigen
        sensor_status = self.sensor_detector.get_sensor_status_message()
        status_color = 'green' if self.pir_available else 'orange'
        ttk.Label(main_frame, text=sensor_status, 
                 foreground=status_color, font=('Arial', 9, 'bold')).grid(row=row, column=0, 
                                                                           columnspan=2, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Radio-Buttons für Modi
        # Prüfe ob aktueller Modus verfügbar ist, sonst wähle ersten verfügbaren
        current_mode = self.config.display_mode
        if current_mode not in self.available_modes:
            current_mode = self.available_modes[0] if self.available_modes else "continuous"
            logger.warning(f"Aktueller Modus '{self.config.display_mode}' nicht verfügbar, wechsle zu '{current_mode}'")
        
        self.vars['display_mode'] = tk.StringVar(value=current_mode)
        
        # Modus 1: PIR-Steuerung (nur wenn Sensor verfügbar)
        mode_frame_1 = ttk.LabelFrame(main_frame, text="Modus 1: PIR Bewegungssensor", padding=10)
        mode_frame_1.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        pir_radio = ttk.Radiobutton(mode_frame_1, text="PIR-Steuerung aktivieren", 
                                    variable=self.vars['display_mode'], 
                                    value="pir")
        pir_radio.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Deaktiviere wenn Sensor nicht verfügbar
        if not self.pir_available:
            pir_radio.config(state='disabled')
            ttk.Label(mode_frame_1, text="⚠️ PIR-Sensor nicht verfügbar", 
                     foreground='red', font=('Arial', 8, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(mode_frame_1, text="• Bildschirm AN bei Bewegung\n"
                                     "• Bildschirm AUS nach Timeout (keine Bewegung)\n"
                                     "• Ideal für Energiesparen",
                 foreground='gray' if self.pir_available else 'lightgray', 
                 font=('Arial', 8)).grid(row=1, column=0, sticky=tk.W, padx=20)
        row += 1
        
        # Modus 2: Zeitsteuerung
        mode_frame_2 = ttk.LabelFrame(main_frame, text="Modus 2: Zeitsteuerung (Arbeitszeit)", padding=10)
        mode_frame_2.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Radiobutton(mode_frame_2, text="Zeitsteuerung aktivieren", 
                       variable=self.vars['display_mode'], 
                       value="time").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        ttk.Label(mode_frame_2, text="• Während Arbeitszeit: Dauerschleife (immer AN)\n"
                                     "• Außerhalb Arbeitszeit: Bildschirm AUS\n"
                                     "• Ideal für Geschäftszeiten",
                 foreground='gray', font=('Arial', 8)).grid(row=1, column=0, sticky=tk.W, padx=20)
        row += 1
        
        # Modus 3: Dauerschleife
        mode_frame_3 = ttk.LabelFrame(main_frame, text="Modus 3: Dauerschleife (24/7)", padding=10)
        mode_frame_3.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Radiobutton(mode_frame_3, text="Dauerschleife aktivieren", 
                       variable=self.vars['display_mode'], 
                       value="continuous").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        ttk.Label(mode_frame_3, text="• Bildschirm IMMER AN (24/7)\n"
                                     "• Bilder laufen durchgehend\n"
                                     "• Ideal für permanente Anzeige",
                 foreground='gray', font=('Arial', 8)).grid(row=1, column=0, sticky=tk.W, padx=20)
        row += 1
        
        # Modus 4: Zeitsteuerung + PIR (nur wenn Sensor verfügbar)
        mode_frame_4 = ttk.LabelFrame(main_frame, text="Modus 4: Zeitsteuerung + PIR (Hybrid)", padding=10)
        mode_frame_4.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        time_pir_radio = ttk.Radiobutton(mode_frame_4, text="Zeitsteuerung + PIR aktivieren", 
                                         variable=self.vars['display_mode'], 
                                         value="time_pir")
        time_pir_radio.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Deaktiviere wenn Sensor nicht verfügbar
        if not self.pir_available:
            time_pir_radio.config(state='disabled')
            ttk.Label(mode_frame_4, text="⚠️ PIR-Sensor nicht verfügbar", 
                     foreground='red', font=('Arial', 8, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(mode_frame_4, text="• Während Arbeitszeit: Dauerschleife (immer AN)\n"
                                     "• Nach Feierabend: PIR-Steuerung (Bewegungssensor)\n"
                                     "• Ideal für flexible Nutzung",
                 foreground='gray' if self.pir_available else 'lightgray',
                 font=('Arial', 8)).grid(row=1, column=0, sticky=tk.W, padx=20)
        row += 1
        
        # === PIR-Einstellungen (nur wenn PIR-Modus) ===
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, 
                                                            sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        ttk.Label(main_frame, text="PIR-Sensor Einstellungen", 
                 font=('Arial', 12, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1
        
        ttk.Label(main_frame, text="(Aktiv bei Modus 1 und Modus 4)", 
                 foreground='gray', font=('Arial', 9)).grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1
        
        # PIR Pin
        ttk.Label(main_frame, text="GPIO Pin (BCM):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vars['pir_pin'] = tk.IntVar(value=self.config.pir_pin)
        ttk.Spinbox(main_frame, from_=0, to=27, textvariable=self.vars['pir_pin'], 
                   width=10).grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # Timeout
        ttk.Label(main_frame, text="Timeout (Sekunden):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vars['screen_timeout'] = tk.IntVar(value=self.config.screen_timeout)
        timeout_frame = ttk.Frame(main_frame)
        timeout_frame.grid(row=row, column=1, sticky=tk.W)
        ttk.Spinbox(timeout_frame, from_=10, to=600, textvariable=self.vars['screen_timeout'], 
                   width=10).pack(side=tk.LEFT)
        ttk.Label(timeout_frame, text="(Zeit bis Bildschirm ausgeht)").pack(side=tk.LEFT, padx=5)
        row += 1
        
        # === Zeitsteuerungs-Einstellungen (nur wenn Zeit-Modus) ===
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, 
                                                            sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        ttk.Label(main_frame, text="Zeitsteuerungs-Einstellungen", 
                 font=('Arial', 12, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1
        
        ttk.Label(main_frame, text="(Aktiv bei Modus 2 und Modus 4)", 
                 foreground='gray', font=('Arial', 9)).grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1
        
        # Arbeitsbeginn
        ttk.Label(main_frame, text="Arbeitsbeginn (HH:MM):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vars['work_start_time'] = tk.StringVar(value=self.config.work_start_time)
        ttk.Entry(main_frame, textvariable=self.vars['work_start_time'], 
                 width=10).grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # Feierabend
        ttk.Label(main_frame, text="Feierabend (HH:MM):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vars['work_end_time'] = tk.StringVar(value=self.config.work_end_time)
        ttk.Entry(main_frame, textvariable=self.vars['work_end_time'], 
                 width=10).grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # === Allgemeine Einstellungen ===
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, 
                                                            sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        ttk.Label(main_frame, text="Allgemeine Einstellungen", 
                 font=('Arial', 12, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1
        
        # Fullscreen
        self.vars['fullscreen'] = tk.BooleanVar(value=self.config.fullscreen)
        ttk.Checkbutton(main_frame, text="Vollbildmodus (ohne Ränder)", 
                       variable=self.vars['fullscreen']).grid(row=row, column=0, 
                                                               columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Mauszeiger verstecken
        self.vars['hide_cursor'] = tk.BooleanVar(value=getattr(self.config, 'hide_cursor', True))
        ttk.Checkbutton(main_frame, text="Mauszeiger in Slideshow verstecken", 
                       variable=self.vars['hide_cursor']).grid(row=row, column=0, 
                                                                columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Status anzeigen
        self.vars['show_sensor_status'] = tk.BooleanVar(value=self.config.show_sensor_status)
        ttk.Checkbutton(main_frame, text="Status-Informationen in Slideshow anzeigen", 
                       variable=self.vars['show_sensor_status']).grid(row=row, column=0, 
                                                                       columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # === Bilder Einstellungen ===
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, 
                                                            sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        ttk.Label(main_frame, text="Bilder", 
                 font=('Arial', 12, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1
        
        # Bildordner
        ttk.Label(main_frame, text="Bildordner:").grid(row=row, column=0, sticky=tk.W, pady=5)
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=row, column=1, sticky=(tk.W, tk.E))
        self.vars['image_folder'] = tk.StringVar(value=self.config.image_folder)
        ttk.Entry(folder_frame, textvariable=self.vars['image_folder'], 
                 width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="Durchsuchen...", 
                  command=self._browse_folder).pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Anzeigedauer
        ttk.Label(main_frame, text="Anzeigedauer pro Bild (Sekunden):").grid(row=row, column=0, 
                                                                              sticky=tk.W, pady=5)
        self.vars['image_duration'] = tk.IntVar(value=self.config.image_duration)
        ttk.Spinbox(main_frame, from_=1, to=60, textvariable=self.vars['image_duration'], 
                   width=10).grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # Zufällige Reihenfolge
        self.vars['random_order'] = tk.BooleanVar(value=self.config.random_order)
        ttk.Checkbutton(main_frame, text="Zufällige Reihenfolge", 
                       variable=self.vars['random_order']).grid(row=row, column=0, 
                                                                 columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # === System Einstellungen ===
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, 
                                                            sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        ttk.Label(main_frame, text="System", 
                 font=('Arial', 12, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1
        
        # Autostart
        self.vars['autostart'] = tk.BooleanVar(value=self.config.autostart)
        ttk.Checkbutton(main_frame, text="Automatisch beim Systemstart starten", 
                       variable=self.vars['autostart']).grid(row=row, column=0, 
                                                              columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Debug
        self.vars['debug_mode'] = tk.BooleanVar(value=self.config.debug_mode)
        ttk.Checkbutton(main_frame, text="Debug-Modus", 
                       variable=self.vars['debug_mode']).grid(row=row, column=0, 
                                                               columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # === Buttons ===
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, 
                                                            sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="💾 Speichern", 
                  command=self._save_config, width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="▶ START", 
                  command=self._start_slideshow, width=18, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Beenden", 
                  command=self._quit, width=18).pack(side=tk.LEFT, padx=5)
        
        # Info-Text
        row += 1
        info_text = "Hinweis: Drücken Sie ESC während der Slideshow, um zur Konfiguration zurückzukehren."
        ttk.Label(main_frame, text=info_text, foreground='blue', 
                 wraplength=700).grid(row=row, column=0, columnspan=2, pady=10)
        
        # Style für Accent Button
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
    
    def _load_values(self):
        """Lädt die Werte aus der Konfiguration"""
        # Bereits in _create_widgets gemacht
        pass
    
    def _browse_folder(self):
        """Öffnet Dateiauswahl für Bildordner"""
        folder = filedialog.askdirectory(
            title="Bildordner auswählen",
            initialdir=self.vars['image_folder'].get()
        )
        if folder:
            self.vars['image_folder'].set(folder)
    
    def _save_config(self):
        """Speichert die Konfiguration"""
        try:
            # Validiere Display-Modus
            display_mode = self.vars['display_mode'].get()
            if not self.config_manager.validate_display_mode(display_mode):
                messagebox.showerror("Fehler", 
                                   f"Ungültiger Display-Modus: {display_mode}\n"
                                   "Bitte wähle einen gültigen Modus!")
                return
            
            # Prüfe ob Modus verfügbar ist
            if display_mode not in self.available_modes:
                messagebox.showerror("Fehler", 
                                   f"Modus '{display_mode}' ist nicht verfügbar!\n\n"
                                   f"Grund: PIR-Sensor nicht erkannt.\n"
                                   f"Verfügbare Modi: {', '.join(self.available_modes)}")
                return
            
            # Hole hide_cursor Wert (mit Fallback)
            try:
                hide_cursor_value = self.vars['hide_cursor'].get()
            except:
                hide_cursor_value = True
            
            # Erstelle neue Config mit Werten aus GUI
            new_config = AppConfig(
                display_mode=display_mode,
                pir_pin=self.vars['pir_pin'].get(),
                screen_timeout=self.vars['screen_timeout'].get(),
                work_start_time=self.vars['work_start_time'].get(),
                work_end_time=self.vars['work_end_time'].get(),
                image_folder=self.vars['image_folder'].get(),
                image_duration=self.vars['image_duration'].get(),
                random_order=self.vars['random_order'].get(),
                autostart=self.vars['autostart'].get(),
                fullscreen=self.vars['fullscreen'].get(),
                hide_cursor=hide_cursor_value,
                debug_mode=self.vars['debug_mode'].get(),
                show_sensor_status=self.vars['show_sensor_status'].get()
            )
            
            # Speichern
            if self.config_manager.save(new_config):
                self.config = new_config
                logger.info("Konfiguration gespeichert (Speichern-Button)")
                # Zeige Erfolg-Meldung
                messagebox.showinfo("Erfolg", "Konfiguration erfolgreich gespeichert!")
            else:
                messagebox.showerror("Fehler", "Konfiguration konnte nicht gespeichert werden!")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
            logger.error(f"Fehler beim Speichern der Konfiguration: {e}")
    
    def _start_slideshow(self):
        """Startet die Slideshow"""
        try:
            # Validiere und speichere Config OHNE Messagebox
            display_mode = self.vars['display_mode'].get()
            
            # Validierung
            if not self.config_manager.validate_display_mode(display_mode):
                messagebox.showerror("Fehler", 
                                   f"Ungültiger Display-Modus: {display_mode}\n"
                                   "Bitte wähle einen gültigen Modus!")
                return
            
            if display_mode not in self.available_modes:
                messagebox.showerror("Fehler", 
                                   f"Modus '{display_mode}' ist nicht verfügbar!\n\n"
                                   f"Grund: PIR-Sensor nicht erkannt.\n"
                                   f"Verfügbare Modi: {', '.join(self.available_modes)}")
                return
            
            # Hole hide_cursor Wert (mit Fallback)
            try:
                hide_cursor_value = self.vars['hide_cursor'].get()
            except:
                hide_cursor_value = True
            
            # Erstelle neue Config
            new_config = AppConfig(
                display_mode=display_mode,
                pir_pin=self.vars['pir_pin'].get(),
                screen_timeout=self.vars['screen_timeout'].get(),
                work_start_time=self.vars['work_start_time'].get(),
                work_end_time=self.vars['work_end_time'].get(),
                image_folder=self.vars['image_folder'].get(),
                image_duration=self.vars['image_duration'].get(),
                random_order=self.vars['random_order'].get(),
                autostart=self.vars['autostart'].get(),
                fullscreen=self.vars['fullscreen'].get(),
                hide_cursor=hide_cursor_value,
                debug_mode=self.vars['debug_mode'].get(),
                show_sensor_status=self.vars['show_sensor_status'].get()
            )
            
            # Speichern (OHNE Messagebox!)
            if not self.config_manager.save(new_config):
                messagebox.showerror("Fehler", "Konfiguration konnte nicht gespeichert werden!")
                return
            
            self.config = new_config
            logger.info("Konfiguration gespeichert, starte Slideshow...")
            
            # WICHTIG: Callback ZUERST aufrufen, DANN Fenster verstecken
            # Sonst wird die Messagebox blockiert
            if self.on_start_callback:
                # Verstecke Fenster VOR dem Callback
                self.root.withdraw()
                # Rufe Callback auf (startet Slideshow)
                self.on_start_callback()
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Starten: {e}")
            logger.error(f"Fehler beim Starten der Slideshow: {e}")
            # Bei Fehler Fenster wieder anzeigen
            self.root.deiconify()
    
    def _quit(self):
        """Beendet die Anwendung"""
        if messagebox.askokcancel("Beenden", "Möchten Sie die Anwendung wirklich beenden?"):
            self.root.destroy()
            import sys
            sys.exit(0)
    
    def show(self):
        """Zeigt das Konfigurationsfenster"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def hide(self):
        """Versteckt das Konfigurationsfenster"""
        self.root.withdraw()
    
    def run(self):
        """Startet die GUI-Hauptschleife"""
        self.root.mainloop()


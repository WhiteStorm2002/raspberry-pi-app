#!/usr/bin/env python3
"""
Slideshow-Verwaltung für Bildanzeige
"""

import os
import random
import logging
from pathlib import Path
from typing import List, Optional
from PIL import Image, ImageTk
import tkinter as tk

logger = logging.getLogger(__name__)


class Slideshow:
    """Klasse für die Slideshow-Verwaltung"""
    
    SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    
    def __init__(self, image_folder: str, random_order: bool = False):
        """
        Initialisiert die Slideshow
        
        Args:
            image_folder: Pfad zum Ordner mit Bildern
            random_order: True für zufällige Reihenfolge
        """
        self.image_folder = Path(image_folder)
        self.random_order = random_order
        self.images: List[Path] = []
        self.current_index = 0
        self.current_image = None
        self.current_photo = None
        
        self.load_images()
        logger.info(f"Slideshow initialisiert mit {len(self.images)} Bildern")
    
    def load_images(self):
        """Lädt alle Bilder aus dem Ordner"""
        self.images = []
        
        if not self.image_folder.exists():
            logger.warning(f"Bildordner existiert nicht: {self.image_folder}")
            self.image_folder.mkdir(parents=True, exist_ok=True)
            return
        
        # Sammle alle unterstützten Bilddateien
        for ext in self.SUPPORTED_FORMATS:
            self.images.extend(self.image_folder.glob(f'*{ext}'))
            self.images.extend(self.image_folder.glob(f'*{ext.upper()}'))
        
        # Sortiere oder mische
        if self.random_order:
            random.shuffle(self.images)
        else:
            self.images.sort()
        
        logger.info(f"{len(self.images)} Bilder geladen")
    
    def reload_images(self):
        """Lädt die Bilderliste neu"""
        old_count = len(self.images)
        self.load_images()
        logger.info(f"Bilder neu geladen: {old_count} -> {len(self.images)}")
    
    def get_next_image(self) -> Optional[Path]:
        """Gibt den Pfad zum nächsten Bild zurück"""
        if not self.images:
            logger.warning("Keine Bilder verfügbar")
            return None
        
        image_path = self.images[self.current_index]
        
        # Nächster Index
        self.current_index = (self.current_index + 1) % len(self.images)
        
        return image_path
    
    def get_previous_image(self) -> Optional[Path]:
        """Gibt den Pfad zum vorherigen Bild zurück"""
        if not self.images:
            return None
        
        self.current_index = (self.current_index - 2) % len(self.images)
        return self.get_next_image()
    
    def load_image_for_display(self, image_path: Path, width: int, height: int) -> Optional[ImageTk.PhotoImage]:
        """
        Lädt ein Bild und skaliert es für die Anzeige
        
        Args:
            image_path: Pfad zum Bild
            width: Zielbreite
            height: Zielhöhe
            
        Returns:
            PhotoImage für Tkinter oder None bei Fehler
        """
        try:
            # Lade Bild
            img = Image.open(image_path)
            
            # Berechne Skalierung (aspect ratio beibehalten)
            img_ratio = img.width / img.height
            screen_ratio = width / height
            
            if img_ratio > screen_ratio:
                # Bild ist breiter
                new_width = width
                new_height = int(width / img_ratio)
            else:
                # Bild ist höher
                new_height = height
                new_width = int(height * img_ratio)
            
            # Skaliere Bild
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Konvertiere für Tkinter
            photo = ImageTk.PhotoImage(img)
            
            self.current_image = img
            self.current_photo = photo
            
            return photo
            
        except Exception as e:
            logger.error(f"Fehler beim Laden von {image_path}: {e}")
            return None
    
    def get_image_count(self) -> int:
        """Gibt die Anzahl der Bilder zurück"""
        return len(self.images)
    
    def get_current_index(self) -> int:
        """Gibt den aktuellen Index zurück"""
        return self.current_index
    
    def set_random_order(self, random_order: bool):
        """Setzt die Reihenfolge (zufällig oder sortiert)"""
        if self.random_order != random_order:
            self.random_order = random_order
            self.load_images()


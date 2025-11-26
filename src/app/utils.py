#!/usr/bin/env python3
"""
Hilfsfunktionen für die Raspberry Pi App
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Optional, List


def run_command(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """
    Führt einen Shell-Befehl aus
    
    Args:
        cmd: Liste mit Befehl und Argumenten
        check: Wenn True, wird bei Fehler eine Exception geworfen
        
    Returns:
        CompletedProcess-Objekt mit Ergebnis
    """
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=True,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen von {' '.join(cmd)}: {e}")
        if check:
            raise
        return e


def is_raspberry_pi() -> bool:
    """Prüft, ob das System ein Raspberry Pi ist"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
    except FileNotFoundError:
        return False


def is_root() -> bool:
    """Prüft, ob das Skript mit Root-Rechten läuft"""
    return os.geteuid() == 0


def check_python_version(min_version: tuple = (3, 7)) -> bool:
    """
    Prüft die Python-Version
    
    Args:
        min_version: Minimale erforderliche Version als Tuple (major, minor)
        
    Returns:
        True wenn Version ausreichend ist
    """
    current = sys.version_info[:2]
    return current >= min_version


def create_directory(path: Path, sudo: bool = False) -> bool:
    """
    Erstellt ein Verzeichnis
    
    Args:
        path: Pfad zum Verzeichnis
        sudo: Wenn True, wird sudo verwendet
        
    Returns:
        True bei Erfolg
    """
    try:
        if sudo and not is_root():
            run_command(['sudo', 'mkdir', '-p', str(path)])
        else:
            path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Fehler beim Erstellen von {path}: {e}")
        return False


def get_system_info() -> dict:
    """Gibt Systeminformationen zurück"""
    info = {
        'is_raspberry_pi': is_raspberry_pi(),
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'is_root': is_root(),
    }
    
    try:
        # Raspberry Pi Modell
        with open('/proc/device-tree/model', 'r') as f:
            info['model'] = f.read().strip('\x00')
    except FileNotFoundError:
        info['model'] = 'Unbekannt'
    
    return info


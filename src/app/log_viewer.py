#!/usr/bin/env python3
"""
Log-Viewer für Crash-Reports und Error-Logs
Kann als eigenständiges Tool verwendet werden
"""

import sys
from pathlib import Path
from datetime import datetime
import argparse


def list_logs(log_dir: Path, log_type: str = 'all'):
    """
    Listet alle Logs auf
    
    Args:
        log_dir: Log-Verzeichnis
        log_type: 'crash', 'error' oder 'all'
    """
    crash_dir = log_dir / 'crashes'
    error_dir = log_dir / 'errors'
    
    print("\n" + "="*70)
    print("📋 LOG-ÜBERSICHT")
    print("="*70 + "\n")
    
    if log_type in ['crash', 'all']:
        print("💥 CRASH-REPORTS:")
        print("-" * 70)
        crashes = sorted(crash_dir.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if crashes:
            for i, crash_file in enumerate(crashes, 1):
                mtime = datetime.fromtimestamp(crash_file.stat().st_mtime)
                size = crash_file.stat().st_size
                print(f"{i:3d}. {crash_file.name:50s} {mtime.strftime('%d.%m.%Y %H:%M')} ({size:,} bytes)")
        else:
            print("  Keine Crash-Reports gefunden ✓")
        print()
    
    if log_type in ['error', 'all']:
        print("⚠️  ERROR-REPORTS:")
        print("-" * 70)
        errors = sorted(error_dir.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if errors:
            # Zeige nur die neuesten 20
            for i, error_file in enumerate(errors[:20], 1):
                mtime = datetime.fromtimestamp(error_file.stat().st_mtime)
                size = error_file.stat().st_size
                print(f"{i:3d}. {error_file.name:50s} {mtime.strftime('%d.%m.%Y %H:%M')} ({size:,} bytes)")
            
            if len(errors) > 20:
                print(f"\n  ... und {len(errors) - 20} weitere Error-Reports")
        else:
            print("  Keine Error-Reports gefunden ✓")
        print()
    
    print("="*70)
    print(f"Log-Verzeichnis: {log_dir}")
    print("="*70 + "\n")


def show_log(log_file: Path):
    """
    Zeigt den Inhalt eines Logs an
    
    Args:
        log_file: Pfad zur Log-Datei
    """
    if not log_file.exists():
        print(f"❌ Datei nicht gefunden: {log_file}")
        return
    
    print("\n" + "="*70)
    print(f"📄 {log_file.name}")
    print("="*70 + "\n")
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    
    print("\n" + "="*70 + "\n")


def cleanup_logs(log_dir: Path, days: int = 30, dry_run: bool = False):
    """
    Löscht alte Logs
    
    Args:
        log_dir: Log-Verzeichnis
        days: Alter in Tagen
        dry_run: Wenn True, nur anzeigen ohne zu löschen
    """
    from datetime import timedelta
    
    cutoff_time = datetime.now() - timedelta(days=days)
    
    print("\n" + "="*70)
    print(f"🗑️  LOG-CLEANUP (älter als {days} Tage)")
    print("="*70 + "\n")
    
    deleted_count = 0
    total_size = 0
    
    for log_type, subdir in [('Crash', 'crashes'), ('Error', 'errors')]:
        log_subdir = log_dir / subdir
        old_logs = []
        
        for log_file in log_subdir.glob('*.md'):
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff_time:
                size = log_file.stat().st_size
                old_logs.append((log_file, mtime, size))
        
        if old_logs:
            print(f"{log_type}-Reports:")
            for log_file, mtime, size in old_logs:
                print(f"  - {log_file.name} ({mtime.strftime('%d.%m.%Y')}, {size:,} bytes)")
                total_size += size
                deleted_count += 1
                
                if not dry_run:
                    log_file.unlink()
            print()
    
    if deleted_count > 0:
        action = "Würden gelöscht werden" if dry_run else "Gelöscht"
        print(f"{action}: {deleted_count} Dateien ({total_size:,} bytes)")
    else:
        print("Keine alten Logs gefunden ✓")
    
    print("\n" + "="*70 + "\n")


def main():
    """Hauptfunktion für Log-Viewer CLI"""
    parser = argparse.ArgumentParser(
        description='Log-Viewer für Raspberry Pi Eingangsbereich Display',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s list                    # Alle Logs auflisten
  %(prog)s list --type crash       # Nur Crash-Reports
  %(prog)s show crash-*.md         # Crash-Report anzeigen
  %(prog)s cleanup --days 30       # Logs älter als 30 Tage löschen
  %(prog)s cleanup --dry-run       # Zeige was gelöscht würde
        """
    )
    
    parser.add_argument(
        'command',
        choices=['list', 'show', 'cleanup'],
        help='Befehl'
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='Log-Datei (für show-Befehl)'
    )
    
    parser.add_argument(
        '--type',
        choices=['crash', 'error', 'all'],
        default='all',
        help='Log-Typ (Standard: all)'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Alter in Tagen für Cleanup (Standard: 30)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Zeige was gelöscht würde ohne zu löschen'
    )
    
    parser.add_argument(
        '--log-dir',
        type=Path,
        default=Path.home() / '.local' / 'share' / 'raspi-app' / 'logs',
        help='Log-Verzeichnis'
    )
    
    args = parser.parse_args()
    
    # Prüfe ob Log-Verzeichnis existiert
    if not args.log_dir.exists():
        print(f"❌ Log-Verzeichnis nicht gefunden: {args.log_dir}")
        print("Tipp: Starte die Anwendung mindestens einmal um Logs zu erstellen.")
        sys.exit(1)
    
    # Führe Befehl aus
    if args.command == 'list':
        list_logs(args.log_dir, args.type)
    
    elif args.command == 'show':
        if not args.file:
            print("❌ Bitte gib eine Log-Datei an!")
            print("Beispiel: log-viewer show crash-20251126-143022.md")
            sys.exit(1)
        
        # Suche Datei in crash/error Verzeichnissen
        log_file = None
        for subdir in ['crashes', 'errors']:
            potential_file = args.log_dir / subdir / args.file
            if potential_file.exists():
                log_file = potential_file
                break
        
        if log_file:
            show_log(log_file)
        else:
            print(f"❌ Log-Datei nicht gefunden: {args.file}")
            sys.exit(1)
    
    elif args.command == 'cleanup':
        cleanup_logs(args.log_dir, args.days, args.dry_run)


if __name__ == '__main__':
    main()


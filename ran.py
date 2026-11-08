"""
File Organizer - sorts files by extension.

Usage:
    python organizer.py
    python organizer.py --dry-run
    python organizer.py --undo

See README.md for Task Scheduler setup.
"""
import argparse
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

# this is for base path which made for download folder but you can use for every other direction

BASE = Path(os.getenv("ORGANIZER_BASE", Path.home() / "Downloads"))

# this is for log file, fill the path

LOGS = Path(os.getenv("ORGANIZER_LOGS", Path.home() / "Desktop" / "my_orgnizer"))
LOGS.mkdir(exist_ok=True, parents=True)

HISTORY = LOGS / 'history.json'

DESTINATIONS = {
    # Documents
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".xls": "Documents",
    ".xlsx": "Documents",
    ".ppt": "Documents",
    ".pptx": "Documents",
    ".txt": "Documents",
    # Music
    ".mp3": "Musics",
    ".wav": "Musics",
    ".flac": "Musics",
    ".m4a": "Musics",
    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".webp": "Images",
    ".svg": "Images",
    # Videos
    ".mp4": "Videos",
    ".mkv": "Videos",
    ".avi": "Videos",
    ".mov": "Videos",
    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    # Code
    ".py": "Codes",
    ".js": "Codes",
    ".html": "Codes",
    ".css": "Codes",
    ".json": "Codes",
    ".sql": "Codes",
    # Apps
    ".exe": "Apps",
    ".msi": "Apps",
    ".apk": "Apps",
}

def load_history() -> list:
    if not HISTORY.exists():
        return []
    try:
        with open(HISTORY, encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("History file is corrupt, starting again!")
        return []
    
def save_history(history: list) -> None:
    with open(HISTORY, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def organize(dry_run: bool = False) -> None:

    now = datetime.now()

    for folder in set(DESTINATIONS.values()):
        (BASE / folder).mkdir(exist_ok=True, parents=True)

    moved = set()
    skipped = set()
    existed = set()
    moved_pairs = []

    try:
        for item in BASE.iterdir():
            if not item.is_file():
                continue

            ext = item.suffix.lower()
            folder_name = DESTINATIONS.get(ext)
            if not folder_name:
                skipped.add(item.name)
                continue

            dst = BASE / folder_name / item.name

            if dst.exists():
                existed.add(item.name)
                continue

            if dry_run:
                print(f"[DRY] {item.name} → {folder_name}/")
                moved.add(item.name)
                moved_pairs.append((item.name, folder_name))
            else:    
                try:
                    shutil.move(str(item), str(dst))
                    moved.add(item.name)
                    moved_pairs.append((item.name, folder_name))
                except OSError as e:
                    print(f'Failed: {item.name} error: {e}')
                    skipped.add(item.name)

        label = "Would move" if dry_run else "Moved"
        print("-" * 50)
        print(f"{label}: {len(moved)}")
        print(f"Existed: {len(existed)}")
        print(f"Skipped: {len(skipped)}")
        print("-" * 50)

        if dry_run:
            print("\n DRY RUN - No files were moved!")
            return

        history = load_history()
        history.append({
            "date": now.isoformat(),
            "moved": [[name, folder] for name, folder in moved_pairs]
        })
        save_history(history)

        lines = []
        lines.append('=' * 50)
        lines.append(f'Runtime: {now:%Y-%m-%d %H:%M:%S}')
        lines.append('=' * 50)

        for folder in sorted(set(DESTINATIONS.values())):
            path = BASE / folder
            if not path.exists():
                continue

            files = [f for f in path.iterdir() if f.is_file()]
            if not files:
                continue

            lines.append(f'📁 {folder}/')
            for f in sorted(files, key=lambda p: p.name.lower()):
                if f.name in moved:
                    lines.append(f'✅ {f.name} | MOVED | {now:%H:%M:%S}')
                elif f.name in existed:
                    lines.append(f'⏸️ {f.name} | EXISTED')
            lines.append("")

        if skipped:
            lines.append("Skipped (remain in root):")
            for name in sorted(skipped, key=str.lower):
                lines.append(f"❌ {name}")
            lines.append("")

        log = LOGS / "Report.log"
        try:
            with open(log, "a", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")   
        except FileNotFoundError as e:
            print(f'Error: {e}')
        except PermissionError as e:
            print(f'Error: {e}')

    except (shutil.Error, OSError) as e:
        print(f'Error: {e}')




def undo() -> None:
    history = load_history()
    if not history:
        print("No history to undo!")
        return
    last = history.pop()
    now = datetime.now()
    lines = [
        "=" * 50,
        f"Undo at: {now:%Y-%m-%d %H:%M:%S}",
        f"Original run: {last['date']}",
        "=" * 50,
        "",
    ]
    count = 0
    for name, folder in last["moved"]:
        src = BASE / folder / name
        dst = BASE / name
        if not src.exists():
            lines.append(f"⚠️ SKIPPED (not found): {folder}/{name}")
            continue

        try:
            shutil.move(str(src), str(dst))
            lines.append(f"↩️ Restored: {folder}/{name} → {name}")
            count += 1
        except OSError as e:
            lines.append(f"❌ FAILED: {folder}/{name} | {e}")

    lines.append("")
    lines.append("-" * 50)
    lines.append(f"Total restored: {count} / {len(last['moved'])}")
    lines.append("=" * 50)
    lines.append("")

    log = LOGS / "Undo.log"
    with open(log, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    save_history(history)
    print(f"✅ Restored {count} files → {log.name}")

def main():
    parser = argparse.ArgumentParser(description="File Organizer By Extensions")
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show What would be moved, existed and skipped.(no actual move)',
    )
    parser.add_argument('--undo', action='store_true', help='Restore everthing that is moved.')
    args = parser.parse_args()

    if args.undo:
        undo()
    else:    
        organize(dry_run=args.dry_run)

if __name__ == '__main__':
    main()
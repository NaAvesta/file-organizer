"""
File Organizer - sorts files by extension.

Usage:
    python organizer.py

See README.md for Task Scheduler setup.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# this is for base path which made for download folder but you can use for every other direction

BASE = Path(os.getenv("ORGANIZER_BASE", Path.home() / "Downloads"))

# this is for log file, fill the path

LOGS = Path(os.getenv("ORGANIZER_LOGS", Path.home() / "Desktop" / "my_orgnizer"))
LOGS.mkdir(exist_ok=True, parents=True)

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

def organize():

    now = datetime.now()

    for folder in set(DESTINATIONS.values()):
        (BASE / folder).mkdir(exist_ok=True, parents=True)

    moved = set()
    skipped = set()
    existed = set()

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
            try:
                shutil.move(str(item), str(dst))
                moved.add(item.name)
            except OSError as e:
                print(f'Failed: {item.name} error: {e}')    

        print("-" * 50)
        print(f"Moved: {len(moved)}")
        print(f"Existed: {len(existed)}")
        print(f"Skipped: {len(skipped)}")
        print("-" * 50)

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
        skipped.add(item.name)

if __name__ == '__main__':
    organize()
"""
File Organizer - sorts files by extension.

Usage:
    python organizer.py <folder>
    python organizer.py <folder> --dry-run
    python organizer.py --undo [folder]

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
            data = json.load(f)
    except json.JSONDecodeError:
        print("History file is corrupt, starting again!")
        return []

    if not isinstance(data, list):
        print("History file has invalid format, starting again!")
        return []

    return data
    
def save_history(history: list) -> None:
    with open(HISTORY, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def organize(folder: Path, dry_run: bool = False) -> None:
    folder = Path(folder).resolve()
    now = datetime.now()

    moved = set()
    skipped_unknown = set()
    skipped_failed = set()
    existed = set()
    moved_pairs = []

    try:
        for item in folder.iterdir():
            if not item.is_file():
                continue

            ext = item.suffix.lower()
            folder_name = DESTINATIONS.get(ext)
            if not folder_name:
                skipped_unknown.add(item.name)
                continue

            dst = folder / folder_name / item.name

            if dst.exists():
                existed.add(item.name)
                continue

            if dry_run:
                print(f"[DRY] {item.name} → {folder_name}/")
                moved.add(item.name)
                moved_pairs.append((item.name, folder_name))
            else:
                (folder / folder_name).mkdir(exist_ok=True, parents=True)
                try:
                    shutil.move(str(item), str(dst))
                    moved.add(item.name)
                    moved_pairs.append((item.name, folder_name))
                except OSError as e:
                    print(f'Failed: {item.name} error: {e}')
                    skipped_failed.add(item.name)

        label = "Would move" if dry_run else "Moved"
        print("-" * 50)
        print(f"{label}: {len(moved)}")
        print(f"Existed: {len(existed)}")
        print(f"Skipped (unknown): {len(skipped_unknown)}")
        print(f"Failed: {len(skipped_failed)}")
        print("-" * 50)

        if dry_run:
            print("\n DRY RUN - No files were moved!")
            return
        if moved_pairs:
            history = load_history()
            history.append({
                "date": now.isoformat(),
                "base": str(folder),
                "moved": [[name, folder] for name, folder in moved_pairs]
            })
            try:
                save_history(history)
            except OSError as e:
                print(f"⚠️ Warning: could not update history | {e}")
                print("   You may need to run --undo again or fix history.json manually")
    
        lines = []
        lines.append('=' * 50)
        lines.append(f'Runtime: {now:%Y-%m-%d %H:%M:%S}')
        lines.append(f"Folder: {folder}")
        lines.append('=' * 50)

        for subfolder in sorted(set(DESTINATIONS.values())):
            path = folder / subfolder
            if not path.exists():
                continue

            files = [f for f in path.iterdir() if f.is_file()]
            if not files:
                continue

            lines.append(f'📁 {subfolder}/')
            for f in sorted(files, key=lambda p: p.name.lower()):
                if f.name in moved:
                    lines.append(f'✅ {f.name} | MOVED | {now:%H:%M:%S}')
                elif f.name in existed:
                    lines.append(f'⏸️ {f.name} | EXISTED')
            lines.append("")

        if skipped_unknown:
            lines.append("Skipped (unknown extension):")
            for name in sorted(skipped_unknown, key=str.lower):
                lines.append(f"  ❌ {name}")
            lines.append("")
        if skipped_failed:
            lines.append("Failed (move error):")
            for name in sorted(skipped_failed, key=str.lower):
                lines.append(f"  ❌ {name}")
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

def undo(target_folder=None):
    history = load_history()
    if not history:
        print("No history to undo!")
        return
    if target_folder is not None:
        target = Path(target_folder).resolve()
        idx = None
        for i in range(len(history) -1, -1, -1):
            record_base = Path(history[i].get('base', str(BASE))).resolve()
            if record_base == target:
                idx = i
                break

        if idx is None:
            print(f"❌ No history for folder: {target_folder}")
            return
        
        last = history.pop(idx)
    else:
        last = history.pop()
    
    base = Path(last.get("base", str(BASE)))
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
        src = base / folder / name
        dst = base / name
        if not src.exists():
            lines.append(f"⚠️ SKIPPED (not found): {folder}/{name}")
            continue

        try:
            shutil.move(str(src), str(dst))
            lines.append(f"↩️ Restored: {folder}/{name} → {name}")
            count += 1
        except OSError as e:
            lines.append(f"❌ FAILED: {folder}/{name} | {e}")

    removed_folders = []
    if base.exists():
        for subfolder in set(DESTINATIONS.values()):
            subpath = base / subfolder
            if subpath.exists() and subpath.is_dir():
                try:
                    subpath.rmdir()
                    removed_folders.append(subfolder)
                except OSError:
                    pass

    if removed_folders:
        lines.append("")
        lines.append("Removed empty folders:")
        for name in sorted(removed_folders):
            lines.append(f"  🧹 {name}/")

    lines.append("")
    lines.append("-" * 50)
    lines.append(f"Total restored: {count} / {len(last['moved'])}")
    lines.append("=" * 50)
    lines.append("")

    log = LOGS / "Undo.log"
    with open(log, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    try:
        save_history(history)
    except OSError as e:
        print(f"⚠️ Warning: could not update history | {e}")
        print("   You may need to fix history.json manually")
    print(f"✅ Restored {count} files → {log.name}")

def main():
    parser = argparse.ArgumentParser(description="File Organizer By Extensions")
    parser.add_argument(
        'folder',
        nargs='?',
        help='Folder to organize'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show What would be moved, existed and skipped.(no actual move)',
    )
    parser.add_argument(
        '--undo',
        nargs='?',
        const=True,
        default=False,
        metavar='FOLDER',
        help='Undo last operation (optionally for a specific folder)'
    )
    args = parser.parse_args()

    if args.undo:
        if args.undo is True:
            undo()
        else:
            undo(Path(args.undo))    
        return

    if args.folder is None:
        print("❌ Error: folder is required.")
        print("   Usage: python organizer.py <folder> [--dry-run]")
        print("          python organizer.py --undo")
        return

    folder = Path(args.folder)
    if not folder.exists():
        print(f"❌ Folder not found: {folder}")
        return
    if not folder.is_dir():
        print(f"❌ Not a folder: {folder}")
        return

    organize(folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
# File Organizer

A Python script that organizes files by extension.

## Features

- Sorts files into folders (Documents, Images, Musics, Videos, etc.)
- Generates a detailed report with moved/existed files
- No external dependencies (stdlib only)

## Requirements

- Python 3.10+

## Automation (Windows Task Scheduler)

1. Press Win + R, type taskschd.msc, Enter
2. Click Create Basic Task
3. Name: Organize Downloads
4. Trigger: Daily at 9:00 AM
5. Action: Start a program
   - Program: pythonw.exe
   - Arguments: organizer.py
   - Start in: project folder
6. Properties: Run whether user is logged on or not

# Organize a folder
python organizer.py <folder>

# Dry run (preview only)
python organizer.py <folder> --dry-run

# Undo last operation (any folder)
python organizer.py --undo

# Undo last operation for a specific folder
python organizer.py --undo [folder]

## License

MIT

## Usage

```bash
- python organizer.py
 
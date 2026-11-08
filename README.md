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

### Dry run

Preview what would be moved without actually moving anything:

### Undo (restore)

Restore the last organize operation:

## License

MIT

## Usage

```bash
- python organizer.py
 
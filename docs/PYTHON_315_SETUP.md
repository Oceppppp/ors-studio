# Windows Python Setup — ORS Studio v0.4.0

This guide applies to **Desktop/source mode**. Public Web hosting runs in a separate managed Python environment defined in `render.yaml`.

## Requirements

- Windows 10/11 x64.
- Python 3.15.x x64 (Python 3.15.2 is supported by this source configuration).
- Internet access during dependency installation.

## Installation

1. Install Python 3.15.x x64 from the official Python website. Include the Python Launcher (`py`).
2. Extract ORS source to a normal user folder, for example `C:\Users\YourName\Documents\ORS_Studio`.
3. Open the extracted folder in File Explorer.
4. Double-click `setup_windows.bat`. Do not type this filename inside the Python `>>>` prompt.
5. Wait for the script to create `.venv`, install binary wheels, and run `scripts\verify_environment.py`.
6. Double-click `START_ORS.bat`.

## Manual verification

From Command Prompt opened in the project folder:

```cmd
py -3.15 --version
.venv\Scripts\python.exe --version
.venv\Scripts\python.exe scripts\verify_environment.py --python-series 3.15
```

## Troubleshooting

- `NameError: setup_windows is not defined`: you ran the `.bat` file inside Python Shell. Type `exit()` and run it from File Explorer or Command Prompt.
- Python 3.15 not found: verify `py -3.15 --version` and install Python Launcher.
- Wheel resolution fails: confirm Windows x64 and internet access; do not remove `--only-binary` without understanding the native build requirements.
- If `.venv` was made with another Python minor version, `setup_windows.bat` recreates it.

## Important

Python 3.15.2 source setup is separate from a future self-contained installer. The installer build must be run on a Windows GitHub runner and tested on a clean Windows computer before being advertised as available.

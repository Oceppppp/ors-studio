@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
  .venv\Scripts\python.exe -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3,15) else 1)" >nul 2>nul
  if errorlevel 1 (
    echo Existing ORS environment is not Python 3.15. Re-running setup...
    call setup_windows.bat
    if errorlevel 1 exit /b 1
  )
) else (
  call setup_windows.bat
  if errorlevel 1 exit /b 1
)

set "ORS_DATA_DIR=%LOCALAPPDATA%\ORS-Studio"
.venv\Scripts\python.exe run_app.py

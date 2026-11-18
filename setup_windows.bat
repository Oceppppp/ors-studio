@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo ================================================
echo   ORS Studio - Python 3.15 Windows setup
echo ================================================

rem Prefer the Python Launcher and select the 3.15 interpreter explicitly.
set "PYTHON_COMMAND="
where py >nul 2>nul
if not errorlevel 1 (
  py -3.15 -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3,15) else 1)" >nul 2>nul
  if not errorlevel 1 set "PYTHON_COMMAND=py -3.15"
)

rem Fallback for installations where Python 3.15 is exposed as python.exe only.
if not defined PYTHON_COMMAND (
  where python >nul 2>nul
  if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3,15) else 1)" >nul 2>nul
    if not errorlevel 1 set "PYTHON_COMMAND=python"
  )
)

if not defined PYTHON_COMMAND (
  echo ERROR: Python 3.15 was not found.
  echo Detected Python 3.15.2 is supported by this ORS release.
  echo Install Python 3.15.x from https://www.python.org/downloads/windows/
  echo Then open this folder in File Explorer and run setup_windows.bat again.
  pause
  exit /b 1
)

rem Recreate an old virtual environment if it was created with another Python.
if exist ".venv\Scripts\python.exe" (
  .venv\Scripts\python.exe -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3,15) else 1)" >nul 2>nul
  if errorlevel 1 (
    echo Existing .venv is not Python 3.15. Recreating it...
    rmdir /s /q ".venv"
  )
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment with %PYTHON_COMMAND% ...
  %PYTHON_COMMAND% -m venv .venv
  if errorlevel 1 goto failed
)

.venv\Scripts\python.exe --version
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto failed

rem Require wheels so Windows does not unexpectedly try compiling scientific packages.
.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
if errorlevel 1 goto failed

.venv\Scripts\python.exe scripts\verify_environment.py --python-series 3.15
if errorlevel 1 goto failed

echo.
echo Setup complete. Start ORS Studio using START_ORS.bat.
pause
exit /b 0

:failed
echo.
echo ERROR: ORS setup failed.
echo Please copy the complete error output and send it for troubleshooting.
echo Check your internet connection and confirm that Python 3.15.x is installed.
pause
exit /b 1

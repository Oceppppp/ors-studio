@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo ==================================================
echo   ORS Studio 0.4.0 - Windows x64 package builder
echo ==================================================

if not exist ".venv\Scripts\python.exe" call setup_windows.bat
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3,15) else 1)"
if errorlevel 1 (
  echo ERROR: Build environment must use Python 3.15.x. Run setup_windows.bat first.
  exit /b 1
)

.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements-dev.txt
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m pytest -q
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onedir --name ORS-Studio --paths backend --add-data "frontend;frontend" --collect-all numpy --collect-all scipy --collect-all pandas --collect-all openpyxl --collect-all xlsxwriter --collect-all reportlab --collect-all fastapi --collect-all uvicorn --collect-all starlette --collect-all pydantic --collect-all pydantic_core --collect-all multipart run_app.py
if errorlevel 1 exit /b 1

echo.
echo Self-contained folder created: dist\ORS-Studio\
where ISCC.exe >nul 2>nul
if not errorlevel 1 (
  ISCC.exe installer\ORS-Studio.iss
  if errorlevel 1 exit /b 1
  echo Installer created: ORS-Studio-Setup-0.4.0.exe
) else (
  echo Inno Setup is not installed. The portable folder is ready.
  echo Install Inno Setup 6, then compile installer\ORS-Studio.iss.
)
echo.
echo End users do not need Python when using the installer.
pause

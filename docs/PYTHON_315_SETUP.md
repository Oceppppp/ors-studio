# Windows Python Setup — ORS Studio v0.4.0

This guide applies to the Desktop/local source mode, which is the recommended way to try ORS without hosting a public server.

## Requirements

- Windows 10/11 x64.
- Python 3.15.x x64 (Python 3.15.2 is supported by this repository setup).
- Python Launcher (py).
- Internet access during dependency installation.

## Install Python

1. Download Python for Windows from https://www.python.org/downloads/windows/.
2. Choose the 64-bit installer.
3. Ensure Python Launcher is installed.
4. Select Add Python to PATH if offered.
5. Finish installation.

Open a new Command Prompt and verify:

~~~cmd
py -3.15 --version
~~~

Expected output: Python 3.15.x.

## Download and run ORS

1. Open https://github.com/Oceppppp/ors-studio.
2. Click Code → Download ZIP, then extract the ZIP. Or use git clone:

~~~cmd
git clone https://github.com/Oceppppp/ors-studio.git
cd ors-studio
~~~

3. Run setup_windows.bat from File Explorer or Command Prompt:

~~~cmd
setup_windows.bat
~~~

4. When setup completes, run:

~~~cmd
START_ORS.bat
~~~

The browser opens the local application. Keep the terminal window open while using ORS.

## Manual verification

From Command Prompt opened in the project folder:

~~~cmd
py -3.15 --version
.venv\Scripts\python.exe --version
.venv\Scripts\python.exe scripts\verify_environment.py --python-series 3.15
~~~

## Troubleshooting

- NameError: setup_windows is not defined: the .bat file was typed inside Python Shell. Type exit() and run it from File Explorer or Command Prompt.
- Python 3.15 not found: verify py -3.15 --version and install Python Launcher.
- Wheel resolution fails: confirm Windows x64 and internet access; do not remove --only-binary without understanding native build requirements.
- If .venv was created with another Python minor version, setup_windows.bat recreates it.
- If the browser does not open, copy the Local app URL printed in the terminal and open it on the same computer.

## Data location

Windows local data is stored under %LOCALAPPDATA%\ORS-Studio. It is independent for each Windows account and is not automatically uploaded or shared.

## Security note

The local API binds to 127.0.0.1 only. Do not change this to 0.0.0.0 or expose this local, unauthenticated API to the internet or LAN.

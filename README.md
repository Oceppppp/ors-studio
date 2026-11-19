# ORS Studio 0.4.0

**Operations Research Studio** is a modular Operations Research and Quantitative Methods application with 29 registered analysis modules. The recommended way to try ORS is to run it locally from a terminal. Each person runs their own copy on their computer; no cloud account or public server is needed for local use.

**Bahasa Indonesia:** see [README_ID.md](README_ID.md) and the [Indonesian terminal quick-start](docs/QUICK_START_TERMINAL_ID.md).

## Quick start — Windows 10/11

Requirements: Windows 64-bit, Python 3.15.x (3.15.2 is supported), and internet access for the first dependency installation.

1. Download this repository using **Code → Download ZIP**, then extract it. Alternatively, clone it with Git:

   ~~~cmd
   git clone https://github.com/Oceppppp/ors-studio.git
   cd ors-studio
   ~~~

2. Confirm Python is available:

   ~~~cmd
   py -3.15 --version
   ~~~

3. Run the setup script from File Explorer or Command Prompt:

   ~~~cmd
   setup_windows.bat
   ~~~

4. After setup completes, start ORS:

   ~~~cmd
   START_ORS.bat
   ~~~

5. Your browser opens the local application. Keep the terminal window open while using ORS; press Ctrl+C in that window to stop the server.

**Do not type setup_windows.bat at the Python >>> prompt.** Batch files must be run from Windows File Explorer, Command Prompt, or PowerShell.

Full instructions and troubleshooting: [Windows terminal quick-start (Indonesian)](docs/QUICK_START_TERMINAL_ID.md) · [Python 3.15 setup](docs/PYTHON_315_SETUP.md).

## Quick start — macOS / Linux

The repository includes run_local.sh. It creates a local virtual environment when one does not exist, installs the desktop runtime requirements, and starts the local app.

~~~bash
chmod +x run_local.sh
./run_local.sh
~~~

A Python 3 installation and internet connection are needed for the first setup. See the [Developer Guide](docs/DEVELOPER_GUIDE.md) for environment details.

## What local mode means

- The API binds to 127.0.0.1 only. It is intended for the computer running it, not as a public server.
- Projects and datasets are stored in a separate local workspace for each computer user.
- Windows data is stored under %LOCALAPPDATA%\ORS-Studio; macOS/Linux data is stored under ~/.ors-studio by default.
- After dependencies are installed, local calculations can run without a cloud account. Do not share the local URL with friends expecting it to work on their devices.

To let a friend use ORS, send them this public repository link: https://github.com/Oceppppp/ors-studio. They download the same source and run the quick-start steps on their own computer.

## Application capabilities

- 29 registered module keys across Operations Research, Production/Operations Management, and Quantitative Methods.
- CSV and XLSX import, worksheet selection, data preview, validation, and column mapping.
- Single analysis and local batch processing.
- Forecast comparison with MAD, MSE, RMSE, MAPE, and holdout-MAD method selection.
- Charts, analysis history, and Excel, CSV, and PDF exports.
- Separate Public Web code path with Guest/Account sessions and tenant-aware PostgreSQL storage (optional cloud deployment; not required for local use).

The 29 module keys do not imply that every advanced submodel in every POM-QM version is reproduced. See [Module Implementation Scope](docs/MODULE_IMPLEMENTATION_SCOPE.md) for each implemented model and its limitations.

## Development and tests

~~~bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m compileall -q backend run_app.py
~~~

For the local desktop runtime, install dependencies from requirements.txt. For the cloud Web runtime, see requirements-web.txt.

## Optional public Web deployment

The repository also contains a separate multi-user Web edition. It requires a hosted Python API, PostgreSQL, Redis, and a background worker. The optional deployment path is [Netlify + Railway](docs/RAILWAY_NETLIFY_DEPLOYMENT.md). It is not needed to run the local application.

## Documentation

- [Windows terminal quick-start — Indonesian](docs/QUICK_START_TERMINAL_ID.md)
- [Python 3.15 setup and troubleshooting](docs/PYTHON_315_SETUP.md)
- [User Guide](docs/PANDUAN_PENGGUNA.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [Module Catalog](docs/MODULE_CATALOG.md)
- [Module Implementation Scope](docs/MODULE_IMPLEMENTATION_SCOPE.md)
- [Netlify + Railway deployment (optional)](docs/RAILWAY_NETLIFY_DEPLOYMENT.md)
- [Cloud Architecture](docs/CLOUD_ARCHITECTURE.md)
- [Security Model](docs/SECURITY_MODEL.md)

## Data and privacy reminder

Local mode keeps files on the user's computer. If you report a problem on GitHub, never attach passwords, session cookies, private datasets, company data, or personal information.

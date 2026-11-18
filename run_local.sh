#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
fi
export ORS_DATA_DIR="${ORS_DATA_DIR:-$HOME/.ors-studio}"
.venv/bin/python run_app.py

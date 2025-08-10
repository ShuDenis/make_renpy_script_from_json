#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/setup.log"
mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "$(date) – Creating virtual environment in $VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
echo "$(date) – Upgrading pip"
pip install --upgrade pip
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "$(date) – Installing packages from requirements.txt"
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

echo "$(date) – Virtual environment created in $VENV_DIR"

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/run.log"
VENV_DIR="$SCRIPT_DIR/.venv"

mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "$(date) – Starting scenegen"

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Run ./setup.sh first." >&2
    exit 1
fi

source "$VENV_DIR/bin/activate"
python -m scenegen.cli "$@"

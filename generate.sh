#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_DIR="$SCRIPT_DIR/input"
OUTPUT_DIR="$SCRIPT_DIR/output"

mkdir -p "$OUTPUT_DIR"

shopt -s nullglob
for json in "$INPUT_DIR"/*.json; do
    python -m scenegen.cli --in "$json" --out-dir "$OUTPUT_DIR"
done

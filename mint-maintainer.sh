#!/usr/bin/env bash
# Linux Mint System Maintenance Script - Main Entry Point
# This is a wrapper that calls the modular Python implementation

set -Euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Python 3 is available
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install it with: sudo apt install python3"
    exit 1
fi

# Pass all arguments to the Python script
exec python3 "$SCRIPT_DIR/mint-maintainer-modular.py" "$@"

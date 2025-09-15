#!/usr/bin/env bash
# Linux Mint System Maintenance Script - Main Entry Point
# This is a wrapper that calls the modular Python implementation

set -Euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Check if Python 3 is available
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install it with: sudo apt install python3"
    exit 1
fi

# Function to setup virtual environment
setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "🔧 Setting up Python environment for the first time..."
        python3 -m venv "$VENV_DIR"
        "$VENV_DIR/bin/pip" install --upgrade pip >/dev/null 2>&1
        "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/config/requirements.txt" >/dev/null 2>&1
        echo "✅ Setup complete!"
        echo ""
    fi
}

# Use virtual environment Python if it exists, otherwise system Python
if [ -d "$VENV_DIR" ]; then
    PYTHON="$VENV_DIR/bin/python3"
else
    PYTHON="python3"
fi

# Check if running with --manifest option
if [[ $# -eq 2 && "$1" == "--manifest" ]]; then
    # Run the runner script with manifest for logging support
    exec bash "$SCRIPT_DIR/tools/mint-maintainer-runner.sh" "$@"
elif [[ $# -eq 0 || "$1" == "dry-run" ]]; then
    # Check if textual is installed
    if "$PYTHON" -c "import textual" 2>/dev/null; then
        # Launch the interactive TUI
        manifest_path=$("$PYTHON" "$SCRIPT_DIR/src/ui/minty_tui.py")
        
        # If manifest was created (user clicked Run), execute it
        if [[ -n "$manifest_path" && -f "$manifest_path" ]]; then
            "$PYTHON" "$SCRIPT_DIR/src/core/mint-maintainer-modular.py" --manifest "$manifest_path"
            # Clean up the temporary manifest file
            rm -f "$manifest_path"
        fi
    else
        # Try to set up the virtual environment
        setup_venv
        
        # Check again with venv Python
        if "$VENV_DIR/bin/python3" -c "import textual" 2>/dev/null; then
            # Launch the interactive TUI with venv Python
            manifest_path=$("$VENV_DIR/bin/python3" "$SCRIPT_DIR/src/ui/minty_tui.py")
            
            # If manifest was created (user clicked Run), execute it
            if [[ -n "$manifest_path" && -f "$manifest_path" ]]; then
                "$VENV_DIR/bin/python3" "$SCRIPT_DIR/src/core/mint-maintainer-modular.py" --manifest "$manifest_path"
                # Clean up the temporary manifest file
                rm -f "$manifest_path"
            fi
        else
            echo "Error: Failed to set up interactive mode."
            echo "Running in classic mode..."
            exec "$PYTHON" "$SCRIPT_DIR/src/core/mint-maintainer-modular.py" "$@"
        fi
    fi
else
    # Pass through any other arguments
    exec "$PYTHON" "$SCRIPT_DIR/src/core/mint-maintainer-modular.py" "$@"
fi

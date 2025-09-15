#!/usr/bin/env bash
# Linux Mint System Maintenance Script - Runner with Logging
# This script wraps the Python modular implementation with comprehensive logging

set -Euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Logging configuration
# For testing, use project directory. For production, use: "${XDG_STATE_HOME:-$HOME/.local/state}/minty-maintenance"
LOG_ROOT="$SCRIPT_DIR/logs"
RUN_ID="$(date +%Y%m%d-%H%M%S)"
RUN_DIR="$LOG_ROOT/$RUN_ID"

# Create log directories
mkdir -p "$RUN_DIR/modules"

# Log file paths
MASTER_LOG="$RUN_DIR/run.log"
AUDIT_LOG="$RUN_DIR/audit.jsonl"

# Use virtual environment Python if it exists, otherwise system Python
if [ -d "$VENV_DIR" ]; then
    PYTHON="$VENV_DIR/bin/python3"
else
    PYTHON="python3"
fi

# Helper functions for structured logging
begin_module() {
    local module_id="$1"
    echo "::BEGIN module=$module_id ts=$(date -Iseconds)"
}

end_module() {
    local module_id="$1"
    local exit_code="$2"
    echo "::END module=$module_id ts=$(date -Iseconds) rc=$exit_code"
}

log_audit() {
    local event_type="$1"
    shift
    local json_data="$*"
    echo "{\"type\":\"$event_type\",\"ts\":\"$(date -Iseconds)\",$json_data}" >> "$AUDIT_LOG"
}

# Export environment variables for Python script
export MINTY_LOG_DIR="$RUN_DIR"
export MINTY_RUN_ID="$RUN_ID"
export MINTY_TEE="${MINTY_TEE:-1}"

# Parse command line arguments
MANIFEST_PATH=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --manifest)
            MANIFEST_PATH="$2"
            shift 2
            ;;
        dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# If manifest provided, read dry_run value from it
if [[ -n "$MANIFEST_PATH" && -f "$MANIFEST_PATH" ]]; then
    # Extract dry_run value from JSON manifest
    MANIFEST_DRY_RUN=$(python3 -c "import json; print(str(json.load(open('$MANIFEST_PATH'))['dry_run']).lower())" 2>/dev/null || echo "false")
    if [[ "$MANIFEST_DRY_RUN" == "true" ]]; then
        DRY_RUN=true
    fi
fi

# Log run start
log_audit "run_start" "\"run_id\":\"$RUN_ID\",\"dry_run\":$DRY_RUN,\"manifest\":\"${MANIFEST_PATH:-none}\""

# Function to run the Python orchestrator
run_orchestrator() {
    local exit_code=0
    
    # If MINTY_TEE is set, use tee for master logging
    if [[ -n "${MINTY_TEE:-}" ]]; then
        # Ensure master log file exists
        touch "$MASTER_LOG"
        echo "[DEBUG] Master log created at: $MASTER_LOG" >&2
        
        # Redirect both stdout and stderr through tee to master log
        exec 3>&1 4>&2  # Save original stdout/stderr
        exec > >(stdbuf -oL -eL tee -a "$MASTER_LOG" >&3)
        exec 2>&1
        echo "[DEBUG] Tee redirection set up"
    fi
    
    echo "=== Minty Maintenance Run: $RUN_ID ==="
    echo "Dry run: $DRY_RUN"
    echo "Log directory: $RUN_DIR"
    echo ""
    
    # Build Python command
    PYTHON_CMD=("$PYTHON" "$SCRIPT_DIR/src/core/mint-maintainer-modular.py")
    
    if [[ -n "$MANIFEST_PATH" ]]; then
        PYTHON_CMD+=("--manifest" "$MANIFEST_PATH")
    elif [[ "$DRY_RUN" == "true" ]]; then
        PYTHON_CMD+=("dry-run")
    fi
    
    # Execute the Python orchestrator
    "${PYTHON_CMD[@]}" || exit_code=$?
    
    return $exit_code
}

# Main execution
EXIT_CODE=0
run_orchestrator || EXIT_CODE=$?

# Log run end
log_audit "run_end" "\"run_id\":\"$RUN_ID\",\"rc\":$EXIT_CODE"

# Copy final report if it exists
REPORT_DIR="$SCRIPT_DIR/reports"
if [[ -d "$REPORT_DIR" ]]; then
    LATEST_REPORT=$(ls -t "$REPORT_DIR"/*.md 2>/dev/null | head -1)
    if [[ -n "$LATEST_REPORT" ]]; then
        cp "$LATEST_REPORT" "$RUN_DIR/report.txt"
        echo "Report saved to: $RUN_DIR/report.txt"
    fi
fi

# Output final status
echo ""
echo "=== Run Complete ==="
echo "Exit code: $EXIT_CODE"
echo "Logs saved to: $RUN_DIR"

# Ensure all output is flushed to log files
if [[ -n "${MINTY_TEE:-}" ]]; then
    # Restore original stdout/stderr before closing
    exec 1>&3 2>&4
    # Give tee a moment to finish writing
    sleep 1
    echo "[DEBUG] Tee process should have completed"
fi

exit $EXIT_CODE

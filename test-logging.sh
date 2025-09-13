#!/usr/bin/env bash
# Quick test script for the logging feature

echo "Testing minty-maintenance logging feature..."
echo ""

# Create a simple test manifest
MANIFEST_FILE="/tmp/test-manifest.json"
cat > "$MANIFEST_FILE" <<EOF
{
  "dry_run": true,
  "create_timeshift": false,
  "selected": ["sys:update_apt", "apps:update_flatpak"]
}
EOF

echo "Created test manifest: $MANIFEST_FILE"
echo "Selected modules: sys:update_apt, apps:update_flatpak"
echo ""

# Run the maintenance script with logging
echo "Running maintenance with logging..."
bash mint-maintainer-runner.sh --manifest "$MANIFEST_FILE"

# Check if logs were created
LOG_DIR="$HOME/.local/state/minty-maintenance"
if [[ -d "$LOG_DIR" ]]; then
    echo ""
    echo "Logs created in: $LOG_DIR"
    echo "Latest run:"
    ls -la "$LOG_DIR" | tail -2
    
    LATEST_RUN=$(ls -t "$LOG_DIR" | head -1)
    if [[ -n "$LATEST_RUN" ]]; then
        echo ""
        echo "Log files in $LATEST_RUN:"
        ls -la "$LOG_DIR/$LATEST_RUN/"
        
        if [[ -f "$LOG_DIR/$LATEST_RUN/audit.jsonl" ]]; then
            echo ""
            echo "Audit log entries:"
            cat "$LOG_DIR/$LATEST_RUN/audit.jsonl"
        fi
    fi
else
    echo "ERROR: Log directory not created!"
fi

# Clean up
rm -f "$MANIFEST_FILE"
echo ""
echo "Test complete!"

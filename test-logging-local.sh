#!/usr/bin/env bash
# Test script for local logging feature

echo "Testing minty-maintenance logging in project directory..."
echo ""

# Create a simple test manifest
MANIFEST_FILE="/tmp/test-manifest.json"
cat > "$MANIFEST_FILE" <<EOF
{
  "dry_run": true,
  "create_timeshift": false,
  "selected": ["sys:update_apt", "apps:update_flatpak", "health:gpu"]
}
EOF

echo "Created test manifest: $MANIFEST_FILE"
echo "Selected modules: sys:update_apt, apps:update_flatpak, health:gpu"
echo ""

# Run the maintenance script with logging
echo "Running maintenance with logging..."
bash mint-maintainer-runner.sh --manifest "$MANIFEST_FILE"

echo ""
echo "=== Checking logs in project directory ==="
if [[ -d "logs" ]]; then
    echo "Logs directory found!"
    echo ""
    echo "Available runs:"
    ls -la logs/
    
    LATEST_RUN=$(ls -t logs/ | grep -v '\.gitkeep' | head -1)
    if [[ -n "$LATEST_RUN" ]]; then
        echo ""
        echo "Latest run: $LATEST_RUN"
        echo "Contents:"
        ls -la "logs/$LATEST_RUN/"
        
        echo ""
        echo "Module logs:"
        ls -la "logs/$LATEST_RUN/modules/"
        
        if [[ -f "logs/$LATEST_RUN/audit.jsonl" ]]; then
            echo ""
            echo "Audit log entries:"
            cat "logs/$LATEST_RUN/audit.jsonl" | python3 -m json.tool --indent 2 2>/dev/null || cat "logs/$LATEST_RUN/audit.jsonl"
        fi
        
        echo ""
        echo "First 20 lines of master log:"
        head -20 "logs/$LATEST_RUN/run.log"
    fi
else
    echo "ERROR: Logs directory not found!"
fi

# Clean up
rm -f "$MANIFEST_FILE"
echo ""
echo "Test complete! Check logs/ directory for output."

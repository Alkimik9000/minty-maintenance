#!/usr/bin/env bash
# Test script to verify logging fixes

echo "Testing logging fixes..."
echo ""

# Test 1: Dry-run mode
echo "=== TEST 1: Dry-run mode ==="
MANIFEST_FILE="/tmp/test-dryrun-manifest.json"
cat > "$MANIFEST_FILE" <<EOF
{
  "dry_run": true,
  "create_timeshift": false,
  "selected": ["apps:update_snap"]
}
EOF

echo "Running with dry_run=true..."
bash mint-maintainer-runner.sh --manifest "$MANIFEST_FILE"

# Check the latest log
LATEST_RUN=$(ls -t logs/ | grep -v -E '(\.gitkeep|README\.md)' | head -1)
if [[ -n "$LATEST_RUN" ]]; then
    echo ""
    echo "Checking audit log for dry_run value..."
    grep "run_start" "logs/$LATEST_RUN/audit.jsonl" | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
print(f'Dry run in audit log: {data[\"dry_run\"]}')
"
    
    echo ""
    echo "Checking for master log..."
    if [[ -f "logs/$LATEST_RUN/run.log" ]]; then
        echo "✓ Master log exists!"
        echo "First 10 lines:"
        head -10 "logs/$LATEST_RUN/run.log"
    else
        echo "✗ Master log missing!"
    fi
    
    echo ""
    echo "Checking for command logging..."
    if [[ -f "logs/$LATEST_RUN/run.log" ]]; then
        echo "Commands found in log:"
        grep -E "(Command:|Executing\.\.\.)" "logs/$LATEST_RUN/run.log" | head -5
    fi
fi

# Test 2: Non-dry-run mode (still safe, just checking snap)
echo ""
echo ""
echo "=== TEST 2: Non-dry-run mode (snap list only) ==="
MANIFEST_FILE2="/tmp/test-nodryrun-manifest.json"
cat > "$MANIFEST_FILE2" <<EOF
{
  "dry_run": false,
  "create_timeshift": false,
  "selected": ["health:gpu"]
}
EOF

echo "Running with dry_run=false (safe module)..."
bash mint-maintainer-runner.sh --manifest "$MANIFEST_FILE2"

# Clean up
rm -f "$MANIFEST_FILE" "$MANIFEST_FILE2"

echo ""
echo "Test complete! Check the logs/ directory for results."

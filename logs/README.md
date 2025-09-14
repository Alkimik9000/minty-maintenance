# Logs Directory

This directory contains execution logs from minty-maintenance runs.

## Structure

Each run creates a timestamped subdirectory:
```
<YYYYMMDD-HHMMSS>/
├── run.log              # Master log with all output
├── audit.jsonl          # Machine-readable event log
├── report.txt           # Final human-readable report
└── modules/             # Per-module logs
    ├── sys-update_apt.log
    ├── apps-update_flatpak.log
    └── ...
```

## Testing

To test the logging feature:
1. Run the TUI: `./mint-maintainer.sh`
2. Select some modules and click "Run"
3. Watch the live output in the RunView screen
4. Check this directory for the generated logs

## Note

This directory is ignored by git (except for .gitkeep and this README).

# 🍃 Live Run View & Logging Feature

## Overview
This feature adds comprehensive logging and live progress tracking to minty-maintenance, keeping the TUI open during execution with real-time output streaming.

## Key Components

### 1. Bash Runner (`mint-maintainer-runner.sh`)
- Creates timestamped log directories in `./logs/<RUN_ID>/` (project directory for testing)
- Implements tee strategy for capturing all output
- Emits structured markers (`::BEGIN` and `::END`) for module tracking
- Generates audit.jsonl for machine-readable events
- Creates per-module logs in `modules/` subdirectory

### 2. Python Orchestrator Updates (`mint-maintainer-modular.py`)
- Emits structured markers around each module execution
- Supports per-module output capture when `MINTY_TEE` is set
- Writes to audit log for each module completion

### 3. TUI RunView Screen (`menu/maintenance_tui.py`)
- New `RunView` screen that displays during execution
- Live streaming of subprocess output with color coding
- Progress bar showing module completion
- Elapsed time tracking
- Control buttons: Stop, View Logs, Back to Menu
- Completion summary with success/failure counts

## Log Structure
```
./logs/                          # In project directory for testing
└── <RUN_ID>/
    ├── run.log              # Master log with all output
    ├── audit.jsonl          # Structured event log
    ├── report.txt           # Final human-readable report
    └── modules/
        ├── sys-update_apt.log
        ├── apps-update_flatpak.log
        └── ...
```

## Audit Log Format
```json
{"type":"run_start","run_id":"20241213-143052","dry_run":true,"ts":"2024-12-13T14:30:52-05:00"}
{"type":"module","id":"sys:update_apt","rc":0,"ts":"2024-12-13T14:30:55-05:00"}
{"type":"module","id":"apps:update_flatpak","rc":0,"ts":"2024-12-13T14:31:02-05:00"}
{"type":"run_end","run_id":"20241213-143052","rc":0,"ts":"2024-12-13T14:31:05-05:00"}
```

## Usage
1. Launch the TUI: `./mint-maintainer.sh`
2. Select modules and click "Run"
3. TUI switches to RunView with live output
4. Monitor progress and view logs in real-time
5. On completion, view summary and return to menu

## Benefits
- No more exiting to terminal during execution
- Complete audit trail for every run
- Per-module logs for debugging
- Live progress tracking
- Ability to stop execution mid-run
- Persistent logs for later review

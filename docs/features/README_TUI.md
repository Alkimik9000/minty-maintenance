# 🍃 minty-maintenance Interactive TUI

## Overview

The minty-maintenance toolkit now includes an interactive, mouse-enabled Terminal User Interface (TUI) that provides a modern way to select which maintenance modules to run.

## Features

- **Mouse Support**: Click to toggle checkboxes, expand/collapse groups, and click buttons
- **Keyboard Navigation**: Full keyboard shortcuts for accessibility
- **Tri-State Checkboxes**: Parent groups show partial state when some children are selected
- **Dry-Run Mode**: Safety first - dry-run is enabled by default
- **Timeshift Integration**: Optional system restore points before maintenance
- **Recommended Daily Macro**: One-click setup for daily maintenance tasks

## Usage

### Launch the TUI

Simply run the main script without arguments:

```bash
./mint-maintainer.sh
```

The TUI will launch automatically if Textual is installed. If not, it falls back to classic mode.

### TUI Layout

1. **Header Bar**: Shows application title and current time
2. **Settings Panel** (top):
   - `[x] Dry-run`: Enabled by default for safety
   - `[ ] Create safety checkpoint (Timeshift)`: Available when dry-run is OFF
3. **Module Tree** (center): Organized by category with collapsible groups
4. **Macro Panel** (bottom): Quick presets like "Recommended Daily"
5. **Action Buttons**: Run, Quit, and Reset
6. **Status Line**: Shows count of selected modules

### Keyboard Shortcuts

- `↑/↓`: Navigate between items
- `←/→`: Collapse/expand groups
- `Space/Enter`: Toggle checkbox
- `a`: Select/deselect all modules
- `r`: Reset to defaults
- `Ctrl+Enter`: Run selected modules
- `q/Esc`: Quit without running

### Mouse Actions

- Click checkbox to toggle
- Click group header to expand/collapse
- Click buttons to perform actions

### Module Categories

**🔧 System Maintenance**
- Create safety checkpoint (Timeshift)
- Update APT core packages
- Manage old kernels
- Update device firmware
- Optimize SSD

**📱 Application Management**
- Update Flatpak apps
- Update Snap packages
- Check Homebrew tools
- Update Python packages
- Detect standalone app updates

**🧹 Cleanup Operations**
- Remove orphaned packages
- Clean system logs
- Clean Docker containers/images
- Deep clean (BleachBit)
- Update file search database

**🏥 Health Checks**
- Disk health
- System services
- GPU status
- Automatic updates enabled

### Recommended Daily Macro

The "Recommended Daily" checkbox automatically:
- Turns OFF dry-run mode
- Enables Timeshift checkpoint
- Selects all Application Management tasks
- Adds essential maintenance: APT updates, orphan removal, log cleanup, and search database update

## Technical Details

### Manifest Format

When you click "Run", the TUI creates a JSON manifest:

```json
{
  "dry_run": false,
  "create_timeshift": true,
  "selected": [
    "sys:update_apt",
    "apps:update_flatpak",
    "clean:logs"
  ]
}
```

### Integration

The TUI integrates seamlessly with the existing bash/python infrastructure:
1. TUI writes manifest to temporary file
2. Calls `mint-maintainer.sh --manifest <file>`
3. Modular script executes only selected modules
4. Temporary manifest is cleaned up automatically

## Installation

Install the TUI dependency:

```bash
pip install -r requirements.txt
```

Or just Textual:

```bash
pip install textual==0.79.1
```

## Fallback Mode

If Textual is not installed, the script automatically falls back to classic mode with all modules running sequentially.

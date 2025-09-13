# 🍃 minty-maintenance - Cursor AI Context

## 🚨 IMPORTANT: Git Commit Policy
**COMMIT FREQUENTLY with descriptive messages!**
- After each feature: `git commit -m "Add: feature description"`
- After each fix: `git commit -m "Fix: issue description"`
- After refactoring: `git commit -m "Refactor: what was changed"`
- Keep commits atomic and focused

## Quick Start
```bash
# Run with interactive TUI (default)
./mint-maintainer.sh

# Run in classic mode (all modules)
./mint-maintainer.sh dry-run

# Run with manifest
./mint-maintainer.sh --manifest /path/to/manifest.json
```

## Architecture Overview

### Entry Points
1. **mint-maintainer.sh** - Bash wrapper that:
   - Sets up Python virtual environment automatically
   - Launches TUI if Textual is available
   - Falls back to classic mode if needed

2. **mint-maintainer-modular.py** - Python orchestrator that:
   - Accepts manifest for selective execution
   - Runs maintenance chapters in order
   - Handles dry-run mode

3. **menu/maintenance_tui.py** - Interactive TUI that:
   - Provides mouse/keyboard navigation
   - Creates JSON manifest of selections
   - Supports tri-state checkboxes

### Module Structure
Each maintenance module follows this pattern:

```python
def functionName(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Module description."""
    try:
        # Implementation
        reporter.say("User-friendly message")
        success, output = runner.run("Description", ["command", "args"])
        return success
    except Exception as e:
        reporter.say("Error: " + str(e), is_error=True)
        return False
```

### Key Classes

**MaintenanceReporter** (`scripts/utils/utils.py`):
- Handles all output and report generation
- Methods: `say()`, `setChapterStatus()`, `writeHeader()`, `writeFinalSummary()`

**CommandRunner** (`scripts/utils/utils.py`):
- Executes system commands with dry-run support
- Method: `run(description, command_list)`

### Module Categories & IDs

**System Maintenance** (`sys:*`):
- `sys:timeshift` - Timeshift checkpoint
- `sys:update_apt` - APT updates
- `sys:manage_kernels` - Kernel cleanup
- `sys:update_firmware` - Firmware updates
- `sys:optimize_ssd` - SSD optimization

**Application Management** (`apps:*`):
- `apps:update_flatpak` - Flatpak updates
- `apps:update_snap` - Snap updates
- `apps:check_brew` - Homebrew check
- `apps:update_python` - Python packages
- `apps:scan_standalone` - Standalone apps

**Cleanup Operations** (`clean:*`):
- `clean:orphans` - Remove orphaned packages
- `clean:logs` - Clean system logs
- `clean:docker` - Docker cleanup
- `clean:bleachbit` - Deep clean
- `clean:updatedb` - Update file database

**Health Checks** (`health:*`):
- `health:disk` - Disk health
- `health:services` - Service status
- `health:gpu` - GPU status
- `health:auto_updates` - Update settings

### TUI Features
- **Dry-run by default**: Safety first
- **Timeshift integration**: Only available when dry-run is OFF
- **Recommended Daily macro**: Pre-configured selections
- **Mouse support**: Click anywhere
- **Keyboard shortcuts**: Full navigation

### Development Workflow
1. Test changes with dry-run first
2. Use type annotations everywhere
3. Follow naming conventions strictly
4. Keep functions small and focused
5. Update both TUI and module when adding features

### Common Tasks

**Add a new maintenance module**:
1. Create module file in appropriate category folder
2. Implement function with standard signature
3. Add to `loadChapters()` in mint-maintainer-modular.py
4. Add to TUI groups in maintenance_tui.py

**Modify TUI behavior**:
1. Edit menu/maintenance_tui.py
2. Test with: `python3 menu/maintenance_tui.py`
3. Check CSS and event handling

**Debug issues**:
1. Check reports/ directory for detailed logs
2. Run with dry-run to see what would happen
3. Test individual modules by importing them

### Important Files
- `requirements.txt` - Python dependencies (just Textual)
- `menu/manifest_schema.json` - Example manifest format
- `.venv/` - Virtual environment (auto-created)
- `reports/` - Generated maintenance reports

### Testing Commands
```bash
# Test TUI directly
cd /opt/repos/minty-maintenance
./.venv/bin/python3 menu/maintenance_tui.py

# Test specific module
./.venv/bin/python3 -c "
from scripts.utils.utils import MaintenanceReporter, CommandRunner
from scripts.system.apt_updates import performAptUpdates
reporter = MaintenanceReporter()
runner = CommandRunner(reporter)
performAptUpdates(reporter, runner)
"

# Run in dry-run mode
./mint-maintainer.sh dry-run
```

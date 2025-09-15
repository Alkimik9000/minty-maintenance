# 🍃 minty-maintenance Project Structure

## Overview
This document describes the organized structure of the minty-maintenance project.

## Directory Structure

```
minty-maintenance/
├── docs/                          # Documentation
│   ├── features/                  # Feature documentation
│   │   ├── LOGGING_FEATURE.md    # Logging system documentation
│   │   ├── README_TUI.md         # TUI documentation
│   │   └── REPORT_SAMPLE.md      # Sample report format
│   └── development/              # Development documentation
│       ├── MIGRATIONS.md         # Migration history
│       └── PROJECT_STRUCTURE.md  # This file
├── scripts/                      # Maintenance modules
│   ├── apps/                     # Application management
│   │   ├── flatpak_updates.py
│   │   ├── gnome_extensions.py
│   │   ├── homebrew_updates.py
│   │   ├── python_updates.py
│   │   ├── snap_updates.py
│   │   └── standalone_apps.py
│   ├── cleanup/                  # System cleanup
│   │   ├── deep_clean.py
│   │   ├── docker_cleanup.py
│   │   ├── kernel_cleanup.py
│   │   └── log_cleanup.py
│   ├── health/                   # Health checks
│   │   ├── disk_health.py
│   │   ├── gpu_check.py
│   │   └── system_health.py
│   ├── system/                   # System maintenance
│   │   ├── apt_updates.py
│   │   ├── auto_updates.py
│   │   ├── firmware_updates.py
│   │   ├── package_sanity.py
│   │   ├── search_database.py
│   │   ├── ssd_optimization.py
│   │   └── timeshift_checkpoint.py
│   └── utils/                    # Shared utilities
│       ├── __init__.py
│       └── utils.py
├── tui/                          # Terminal User Interface
│   ├── minty_tui.py             # Main TUI application
│   └── manifest.example.json    # Example manifest format
├── tools/                        # Development and utility tools
│   ├── install-global-command.sh # Global command installer
│   ├── mint-maintainer-runner.sh # Logging-enabled runner
│   ├── minty                    # Global command wrapper
│   └── test-logging-fixes.sh    # Testing script
├── reports/                      # Generated reports (gitignored)
├── .venv/                        # Python virtual environment (gitignored)
├── mint-maintainer.sh            # Main entry point
├── mint-maintainer-modular.py    # Python orchestrator
├── requirements.txt              # Python dependencies
├── Makefile                      # Build automation
├── README.md                     # Main project documentation
├── RULES.md                      # Project rules and conventions
└── LICENSE                       # License file
```

## File Naming Conventions

### Python Files
- **Modules**: `snake_case.py` (e.g., `apt_updates.py`)
- **Functions**: `camelCase` (e.g., `performAptUpdates`)
- **Variables**: `snake_case` (e.g., `user_input`)
- **Classes**: `PascalCase` (e.g., `MaintenanceReporter`)

### Shell Scripts
- **Main scripts**: `kebab-case.sh` (e.g., `mint-maintainer.sh`)
- **Tool scripts**: `kebab-case.sh` (e.g., `install-global-command.sh`)

### Documentation
- **Feature docs**: `UPPERCASE_WITH_UNDERSCORES.md`
- **Development docs**: `UPPERCASE_WITH_UNDERSCORES.md`

### Configuration Files
- **Examples**: `name.example.ext` (e.g., `manifest.example.json`)
- **Templates**: `name.template.ext`

## Key Directories

### `/docs/`
Contains all project documentation organized by type:
- `features/` - User-facing feature documentation
- `development/` - Developer documentation and project structure

### `/scripts/`
Modular maintenance scripts organized by category:
- `system/` - Core system maintenance
- `apps/` - Application management
- `cleanup/` - System cleanup operations
- `health/` - Health monitoring and checks
- `utils/` - Shared utilities and common functions

### `/tui/`
Terminal User Interface components:
- Main TUI application
- Configuration examples
- UI-related documentation

### `/tools/`
Development and utility tools:
- Installation scripts
- Testing utilities
- Development helpers
- Global command wrappers

## Entry Points

1. **`mint-maintainer.sh`** - Main entry point for users
2. **`mint-maintainer-modular.py`** - Python orchestrator
3. **`tui/minty_tui.py`** - Interactive TUI application
4. **`tools/minty`** - Global command wrapper

## Dependencies

- **Python 3.8+** - Core runtime
- **Textual** - TUI framework (auto-installed)
- **Standard Linux tools** - APT, system utilities

## Git Ignore Patterns

- Python cache files (`__pycache__/`, `*.pyc`)
- Virtual environment (`.venv/`)
- Generated reports (`reports/`)
- Log files (`logs/`, `*.log`)
- Cursor AI files (`.cursor*`, `CURSOR_*`)
- Test files (`tools/test-*.sh`)

## Development Workflow

1. **Feature Development**: Add modules to appropriate `/scripts/` category
2. **Documentation**: Update relevant files in `/docs/`
3. **Testing**: Use tools in `/tools/` for testing
4. **Integration**: Update orchestrator and TUI as needed
5. **Deployment**: Use global command installer for distribution

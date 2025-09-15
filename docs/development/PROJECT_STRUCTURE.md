# 🍃 minty-maintenance Project Structure

## Overview
This document describes the organized structure of the minty-maintenance project with minimal home directory clutter.

## Directory Structure

```
minty-maintenance/
├── src/                          # Source code
│   ├── core/                     # Core application logic
│   │   └── mint-maintainer-modular.py  # Main orchestrator
│   ├── modules/                  # Maintenance modules
│   │   ├── apps/                 # Application management
│   │   ├── cleanup/              # System cleanup
│   │   ├── health/               # Health checks
│   │   ├── system/               # System maintenance
│   │   └── utils/                # Shared utilities
│   └── ui/                       # User Interface
│       ├── minty_tui.py         # Terminal User Interface
│       └── manifest.example.json # Example manifest
├── config/                       # Configuration files
│   ├── requirements.txt          # Python dependencies
│   ├── RULES.md                  # Project rules
│   └── Makefile                  # Build automation
├── docs/                         # Documentation
│   ├── features/                 # Feature documentation
│   └── development/              # Development documentation
├── tools/                        # Development and utility tools
│   ├── install-global-command.sh # Global command installer
│   ├── mint-maintainer-runner.sh # Logging-enabled runner
│   ├── minty                    # Global command wrapper
│   └── test-logging-fixes.sh    # Testing script
├── reports/                      # Generated reports (gitignored)
├── .venv/                        # Python virtual environment (gitignored)
├── mint-maintainer.sh            # Main entry point
├── README.md                     # Main project documentation
└── LICENSE                       # License file
```

## File Organization Principles

### 1. **Minimal Root Directory**
Only essential files in the root:
- `mint-maintainer.sh` - Main entry point
- `README.md` - Project overview
- `LICENSE` - Legal information

### 2. **Source Code in `src/`**
All source code organized by purpose:
- `core/` - Main application logic
- `modules/` - Feature modules by category
- `ui/` - User interface components

### 3. **Configuration in `config/`**
All configuration files centralized:
- Dependencies, rules, build files

### 4. **Documentation in `docs/`**
Structured documentation:
- `features/` - User-facing features
- `development/` - Developer information

### 5. **Tools in `tools/`**
Development and utility scripts:
- Installation, testing, development helpers

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
- **Dependencies**: `requirements.txt`

## Key Directories

### `/src/`
Source code organized by functionality:
- `core/` - Main orchestrator and application logic
- `modules/` - Modular maintenance scripts by category
- `ui/` - Terminal User Interface components

### `/config/`
All configuration and build files:
- Python dependencies
- Project rules and conventions
- Build automation

### `/docs/`
Comprehensive documentation:
- `features/` - User-facing feature documentation
- `development/` - Developer documentation and project structure

### `/tools/`
Development and utility tools:
- Installation scripts
- Testing utilities
- Development helpers
- Global command wrappers

## Entry Points

1. **`mint-maintainer.sh`** - Main entry point for users
2. **`src/core/mint-maintainer-modular.py`** - Python orchestrator
3. **`src/ui/minty_tui.py`** - Interactive TUI application
4. **`tools/minty`** - Global command wrapper

## Dependencies

- **Python 3.8+** - Core runtime
- **Textual** - TUI framework (auto-installed)
- **Standard Linux tools** - APT, system utilities

## Path References

### Updated Import Paths
```python
# Old: from scripts.utils.utils import ...
# New: from utils.utils import ...

# Old: scripts.system.apt_updates
# New: system.apt_updates
```

### Updated File Paths
```bash
# TUI: src/ui/minty_tui.py
# Core: src/core/mint-maintainer-modular.py
# Config: config/requirements.txt
# Tools: tools/mint-maintainer-runner.sh
```

## Git Ignore Patterns

- Python cache files (`__pycache__/`, `*.pyc`)
- Virtual environment (`.venv/`)
- Generated reports (`reports/`)
- Log files (`logs/`, `*.log`)
- Cursor AI files (`.cursor*`, `CURSOR_*`)
- Test files (`tools/test-*.sh`)

## Development Workflow

1. **Feature Development**: Add modules to appropriate `/src/modules/` category
2. **Documentation**: Update relevant files in `/docs/`
3. **Testing**: Use tools in `/tools/` for testing
4. **Integration**: Update orchestrator and TUI as needed
5. **Deployment**: Use global command installer for distribution

## Benefits of This Structure

- **Clean Root**: Only essential files visible
- **Logical Grouping**: Related files organized together
- **Scalable**: Easy to add new modules and features
- **Maintainable**: Clear separation of concerns
- **Professional**: Industry-standard project layout
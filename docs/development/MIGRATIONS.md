# Migrations

This document tracks structural changes and migrations in the Mint Maintenance project.

## Template for New Migrations

```markdown
## [Date] - Migration Title

### Overview
Brief description of what changed and why.

### Changes Made
- List of specific changes
- File moves/renames
- Structure modifications

### Migration Steps
1. Step-by-step instructions
2. For users upgrading
3. Any manual interventions needed

### Compatibility Notes
- Backward compatibility considerations
- Breaking changes if any
```

---

## [2024-01-13] - Modular Architecture Migration

### Overview
Migrated from a monolithic 1500+ line bash script to a modular Python-based architecture with separate scripts for each maintenance task.

### Changes Made
- Moved original `mint-maintainer.sh` to `mint-maintainer-original.sh`
- Created new `mint-maintainer.sh` as a bash wrapper
- Added `mint-maintainer-modular.py` as the main orchestrator
- Created directory structure:
  - `scripts/system/` - System-related maintenance
  - `scripts/apps/` - Application updates
  - `scripts/cleanup/` - Cleanup operations
  - `scripts/health/` - Health checks
  - `scripts/utils/` - Common utilities
- Extracted common functions to `scripts/utils/utils.py`
- Split maintenance chapters into individual Python modules

### Migration Steps
1. Pull the latest changes: `git pull`
2. The script usage remains the same: `bash mint-maintainer.sh [dry-run]`
3. No manual intervention required - backward compatibility maintained

### Compatibility Notes
- The command-line interface remains unchanged
- All existing functionality preserved (except Chapter 1 - temporarily disabled)
- Reports generated in the same format
- Python 3 is now required (should be pre-installed on Linux Mint 22)

---

## Future Migrations

_This section will be updated as new migrations occur._

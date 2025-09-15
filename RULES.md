# Project Rules and Guidelines

This document contains living rules and guidelines for the Mint Maintenance project. It will be updated as new patterns and requirements emerge.

## Code Style Rules

### Python Code Standards
1. **Function Naming**: All Python functions MUST use camelCase naming convention
   - ✅ Good: `openShortPosition()`, `calculateSpaceDiff()`
   - ❌ Bad: `open_short_position()`, `calculate_space_diff()`

2. **Variable Naming**: All variables MUST use snake_case format
   - ✅ Good: `report_dir`, `chapter_status`
   - ❌ Bad: `reportDir`, `chapterStatus`

3. **Type Annotations**: All functions MUST include complete type annotations
   - Parameters, return types, and any variables where type is ambiguous
   - Use `Optional[T]` for nullable types
   - Use `List[T]`, `Dict[K, V]`, `Tuple[T, ...]` from typing module

4. **String Formatting**: NO f-strings allowed (for Python 2.x compatibility)
   - ✅ Good: `"Hello " + name` or `"Hello {}".format(name)`
   - ❌ Bad: `f"Hello {name}"`

5. **Function Complexity**: Avoid overly nested functions
   - Break down complex functions into smaller, understandable units
   - Each function should have a single, clear purpose
   - Name functions descriptively

6. **Class Organization**: Classes should be in separate files
   - One class per file for better organization
   - Import classes as needed

7. **Utility Functions**: Generic reusable functions go in `utils.py`
   - Functions used across multiple scripts
   - Common patterns and helpers

## Git Commit Rules

### Conventional Commits
All commits MUST follow Conventional Commits specification:

**Format**: `<type>(<scope>): <description>`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `build`: Build system changes
- `perf`: Performance improvements
- `revert`: Reverting changes

**Examples**:
- `docs(readme): add badges and quickstart`
- `ci: add shellcheck, shfmt, markdownlint workflow`
- `refactor(script): extract report writer into function`
- `feat(report): add dry-run space-delta estimator`
- `chore(rules): seed RULES.md with review loop`

### Commit Frequency
- Commit early and often
- Each logical change should be a separate commit
-o Don't bundle unrelated changes

## Project Structure Rules

### Directory Organization
```
/opt/repos/minty-maintenance/
├── scripts/
│   ├── system/      # System updates, packages, kernels
│   ├── apps/        # Application updates (flatpak, snap, etc.)
│   ├── cleanup/     # Cleanup tasks
│   ├── health/      # Health checks
│   └── utils/       # Common utilities
├── reports/         # Generated reports (gitignored)
├── rules/           # Rule files and schemas
└── .github/         # GitHub workflows and CI
```

### Script Modularity
- Each maintenance chapter is a separate Python module
- Modules are organized by functionality
- Main orchestrator calls individual modules
- Backward compatibility maintained through bash wrapper

## Maintenance Rules

### Chapter Management
1. Chapter 1 (Timeshift) is DISABLED until further notice
2. All other chapters run normally
3. New chapters should follow the existing pattern
4. Each chapter reports success/failure and notes

### Error Handling
- All errors must be caught and explained in user-friendly terms
- Continue execution even if individual chapters fail
- Report all issues in the final summary
- Never leave the system in a broken state

## Documentation Rules

### Required Documentation
- CHANGELOG.md - Keep a Changelog format
- README.md - User-friendly with badges and quickstart
- RULES.md - This file, living document
- REPORT_SAMPLE.md - Example output with narration
- Code comments for complex logic

### Documentation Updates
- Update docs with every significant change
- Keep examples current
- Maintain backwards compatibility notes

## Testing Rules

### Dry Run Mode
- All scripts MUST support dry-run mode
- Dry run shows what would happen without changes
- Test mode clearly indicated in output

### Quality Checks
- Run shellcheck on bash scripts
- Run Python linters on Python code
- Test all chapters in dry-run mode before commits

## Autonomy Rules

### Allowed Without Asking
- Adding/modifying documentation
- CI/CD improvements
- Linting and formatting fixes
- Test additions
- Makefile targets
- Folder reorganization
- Script refactoring for safety/readability

### Requires Discussion
- Changing core functionality
- Removing features
- Breaking changes
- Major architectural decisions

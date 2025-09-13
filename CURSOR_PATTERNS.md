# 🍃 minty-maintenance Code Patterns & Examples

## Common Code Patterns

### 1. Creating a New Maintenance Module

```python
#!/usr/bin/env python3
"""
Module description here.
"""

from typing import List, Tuple
from scripts.utils.utils import MaintenanceReporter, CommandRunner


def yourFunctionName(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """
    Brief description of what this module does.
    
    Args:
        reporter: The maintenance reporter instance
        runner: The command runner instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        reporter.say("🔧 Starting your maintenance task...")
        reporter.say("This explains what we're about to do in friendly terms.")
        
        # Example command execution
        success, output = runner.run(
            "checking system status",
            ["command", "arg1", "arg2"]
        )
        
        if not success:
            reporter.say("❌ Command failed: " + output, is_error=True)
            return False
            
        # Parse output if needed
        lines = output.strip().split('\n')
        for line in lines:
            if "important" in line:
                reporter.say("   • Found: " + line)
        
        reporter.say("✅ Task completed successfully!")
        return True
        
    except Exception as e:
        reporter.say("❌ Error: " + str(e), is_error=True)
        return False
```

### 2. Adding Module to Orchestrator

In `mint-maintainer-modular.py`, add to `loadChapters()`:

```python
{
    'name': 'Your Module Name',
    'module': 'scripts.category.your_module',
    'function': 'yourFunctionName',
    'category': 'system|apps|cleanup|health',
    'module_id': 'category:your_id'
}
```

### 3. Adding to TUI

In `menu/maintenance_tui.py`, add to the appropriate group:

```python
("category:your_id", "Your Module Display Name"),
```

### 4. Command Runner Patterns

```python
# Simple command
success, output = runner.run("updating package list", ["apt", "update"])

# Command with sudo (runner handles password prompts)
success, output = runner.run("installing package", ["sudo", "apt", "install", "-y", "package"])

# Command with pipe (use shell=True carefully)
success, output = runner.run(
    "counting processes",
    ["bash", "-c", "ps aux | grep python | wc -l"]
)

# Check if command exists
if runner.commandExists("docker"):
    success, output = runner.run("listing containers", ["docker", "ps"])
```

### 5. Reporter Patterns

```python
# Basic messages
reporter.say("Starting task...")
reporter.say("⚠️ Warning: This might take a while", is_warning=True)
reporter.say("❌ Error occurred", is_error=True)

# Formatted output
reporter.say("\n📊 System Status:")
reporter.say("   • CPU Usage: 45%")
reporter.say("   • Memory: 8GB / 16GB")
reporter.say("   • Disk: 120GB free")

# Progress indication
reporter.say("🔄 Processing... ", end='')
# Do work
reporter.say("Done!")

# Chapter status
reporter.setChapterStatus(chapter_num, success=True, message="All good")
reporter.setChapterStatus(chapter_num, success=False, message="Needs attention")
```

### 6. Error Handling Patterns

```python
def robustFunction(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Example of robust error handling."""
    try:
        # Check prerequisites
        if not runner.commandExists("required_command"):
            reporter.say("Required command not found. Skipping.", is_warning=True)
            return True  # Not a failure, just skip
        
        # Try main operation
        try:
            success, output = runner.run("main operation", ["command"])
            if not success:
                # Try fallback
                reporter.say("Main method failed, trying alternative...")
                success, output = runner.run("fallback", ["alt_command"])
        except KeyboardInterrupt:
            reporter.say("\n⚠️ Operation cancelled by user", is_warning=True)
            return False
        except Exception as e:
            reporter.say("Unexpected error: " + str(e), is_error=True)
            return False
            
        return success
        
    except Exception as e:
        reporter.say("Fatal error: " + str(e), is_error=True)
        return False
```

### 7. Parsing Command Output

```python
# Parse JSON output
import json

success, output = runner.run("get JSON data", ["command", "--json"])
if success:
    try:
        data = json.loads(output)
        for item in data.get('items', []):
            reporter.say("   • " + item.get('name', 'Unknown'))
    except json.JSONDecodeError:
        reporter.say("Failed to parse JSON output", is_error=True)

# Parse table output
success, output = runner.run("list items", ["command", "list"])
if success:
    lines = output.strip().split('\n')
    # Skip header
    for line in lines[1:]:
        if line.strip():
            columns = line.split()
            if len(columns) >= 2:
                name = columns[0]
                status = columns[1]
                reporter.say("   • {}: {}".format(name, status))

# Parse key-value output
success, output = runner.run("show info", ["command", "info"])
if success:
    for line in output.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            reporter.say("   • {}: {}".format(key.strip(), value.strip()))
```

### 8. Dry-Run Awareness

```python
def dryRunAwareFunction(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Example showing dry-run awareness."""
    
    if runner.dry_run:
        reporter.say("🔍 Checking what would be changed...")
    else:
        reporter.say("🔧 Making actual changes...")
    
    # Runner automatically handles dry-run for commands
    success, output = runner.run("remove packages", ["apt", "autoremove", "-y"])
    
    # For manual operations
    if runner.dry_run:
        reporter.say("   Would delete: /tmp/old_file")
    else:
        import os
        if os.path.exists("/tmp/old_file"):
            os.remove("/tmp/old_file")
            reporter.say("   Deleted: /tmp/old_file")
    
    return True
```

### 9. Integration Testing Pattern

```python
# Test individual module
if __name__ == "__main__":
    from scripts.utils.utils import MaintenanceReporter, CommandRunner
    
    # Test with dry-run
    reporter = MaintenanceReporter(dry_run=True)
    runner = CommandRunner(reporter)
    
    success = yourFunctionName(reporter, runner)
    print("Test result:", "PASS" if success else "FAIL")
```

### 10. Type Annotations Examples

```python
from typing import Dict, List, Optional, Tuple, Union

def complexFunction(
    reporter: MaintenanceReporter,
    runner: CommandRunner,
    packages: List[str],
    options: Optional[Dict[str, str]] = None
) -> Tuple[bool, List[str]]:
    """Example with complex type annotations."""
    
    results: List[str] = []
    opts: Dict[str, str] = options or {}
    
    package_status: Dict[str, bool] = {}
    
    for package in packages:
        cmd: List[str] = ["dpkg", "-l", package]
        success: bool
        output: str
        success, output = runner.run("checking " + package, cmd)
        
        package_status[package] = success
        if success:
            results.append(package)
    
    all_success: bool = all(package_status.values())
    return (all_success, results)
```

## Common Issues & Solutions

### Issue: Module not found
**Solution**: Ensure module is in correct directory and has `__init__.py`

### Issue: TUI not showing module
**Solution**: Check module_id mapping in both files matches exactly

### Issue: Command fails silently
**Solution**: Always check return value and log output

### Issue: Dry-run not working
**Solution**: Use runner.run() for all commands, check runner.dry_run for manual ops

### Issue: Type checker complaints
**Solution**: Add proper type annotations, avoid Any type

## Testing Checklist

- [ ] Module works in dry-run mode
- [ ] Module works in normal mode
- [ ] Error cases handled gracefully
- [ ] User messages are friendly
- [ ] Type annotations complete
- [ ] Module appears in TUI
- [ ] Module can be selected/deselected
- [ ] Status updates correctly

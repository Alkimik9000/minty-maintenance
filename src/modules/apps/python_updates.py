#!/usr/bin/env python3
"""
Chapter 7: Python Tool Updates
Update Python packages and tools, preferring pipx for safety.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner, checkCommandExists
import subprocess


def updatePythonTools(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Update Python tools and packages."""
    reporter.writeChapterHeader(7, "Updating Python Tools")
    
    reporter.say("\n🐍 If you have any Python tools installed, let me" +
                " update them for you...")
    
    chapter_success = True
    
    if not checkCommandExists("pip"):
        reporter.say("No Python package manager found. That's normal if" +
                    " you're not doing any programming.")
        reporter.setChapterStatus(7, True, "Not needed")
        return True
    
    reporter.say("\nPython tools are programming utilities. Even if you're" +
                " not a programmer, some apps might have installed these.")
    
    # Check for pipx (recommended for Ubuntu 24.04)
    if not checkCommandExists("pipx"):
        reporter.say("\nUbuntu 24.04 recommends using pipx for Python tools.")
        success, _ = runner.run(
            "install pipx for safe Python package management",
            ["sudo", "apt", "install", "-y", "pipx"]
        )
        if not success:
            chapter_success = False
    
    reporter.say("\n💡 Note: Ubuntu 24.04 protects system Python. Use pipx" +
                " for installing Python applications safely.")
    
    # Check for pipx-managed applications
    if checkCommandExists("pipx"):
        reporter.say("\nChecking pipx-managed Python applications...")
        pipx_apps = getPipxApplications()
        
        if pipx_apps:
            success, _ = runner.run(
                "upgrade all pipx-managed applications",
                ["pipx", "upgrade-all"]
            )
            if not success:
                chapter_success = False
            reporter.setChapterStatus(7, chapter_success, "Pipx apps checked")
        else:
            reporter.say("No pipx applications installed.")
            reporter.setChapterStatus(7, chapter_success, "System Python protected")
    else:
        reporter.setChapterStatus(7, chapter_success, "System Python protected")
    
    return chapter_success


def getPipxApplications() -> list:
    """Get list of pipx-managed applications."""
    try:
        result = subprocess.run(
            ["pipx", "list"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout and "nothing has been installed" not in result.stdout:
            # Extract app names from pipx list output
            apps = []
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.startswith('   '):  # App lines are indented
                    app_name = line.strip().split()[0]
                    if app_name:
                        apps.append(app_name)
            return apps
        return []
    except:
        return []


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = updatePythonTools(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

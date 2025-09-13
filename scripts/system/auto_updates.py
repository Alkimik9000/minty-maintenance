#!/usr/bin/env python3
"""
Chapter 20: Automatic Updates Check
Verify that automatic security updates are enabled.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner
import subprocess


def checkAutoUpdates(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Check if automatic updates are enabled."""
    reporter.writeChapterHeader(20, "Verifying Automatic Security Updates")
    
    reporter.say("\n🔒 Ubuntu can install security updates automatically" +
                " in the background. Let me check if this is enabled...")
    
    chapter_success = True
    
    # Check if unattended-upgrades is installed
    if not isPackageInstalled("unattended-upgrades"):
        reporter.say("Automatic updates are not installed!", is_error=True)
        reporter.say("I strongly recommend installing this for security:")
        reporter.say("sudo apt install unattended-upgrades")
        reporter.say("Then enable with: sudo dpkg-reconfigure unattended-upgrades")
        reporter.setChapterStatus(20, False, "Not installed")
        return False
    
    # Check if it's enabled
    auto_enabled = checkAutoUpdateEnabled()
    
    if auto_enabled:
        reporter.say("✅ Automatic security updates are ENABLED!")
        reporter.say("Your system installs critical security fixes" +
                    " automatically, keeping you safe.")
        notes = "Auto-updates enabled"
    else:
        reporter.say("⚠️ Automatic updates are DISABLED!", is_error=True)
        reporter.say("I recommend enabling this for better security.")
        reporter.say("To enable: sudo dpkg-reconfigure unattended-upgrades")
        notes = "Auto-updates disabled"
        chapter_success = False
    
    # Show last run time
    last_run = getLastUpdateRun()
    if last_run:
        reporter.say("Last automatic update check: " + last_run)
    
    reporter.setChapterStatus(20, chapter_success, notes)
    return chapter_success


def isPackageInstalled(package_name: str) -> bool:
    """Check if a package is installed."""
    try:
        result = subprocess.run(
            ["dpkg", "-l", package_name],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.startswith('ii') and package_name in line:
                    return True
        return False
    except:
        return False


def checkAutoUpdateEnabled() -> bool:
    """Check if automatic updates are enabled."""
    try:
        result = subprocess.run(
            ["apt-config", "dump"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            for line in result.stdout.split('\n'):
                if "APT::Periodic::Unattended-Upgrade" in line:
                    # Extract the value
                    if '"1"' in line:
                        return True
                    return False
        return False
    except:
        return False


def getLastUpdateRun() -> str:
    """Get the last time automatic updates ran."""
    log_file = "/var/log/unattended-upgrades/unattended-upgrades.log"
    
    try:
        if os.path.exists(log_file):
            # Get last 50 lines and find most recent date
            result = subprocess.run(
                ["tail", "-n", "50", log_file],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.stdout:
                import re
                dates = re.findall(r'\d{4}-\d{2}-\d{2}', result.stdout)
                if dates:
                    return dates[-1]  # Return most recent date
        
        return "unknown"
    except:
        return "unknown"


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = checkAutoUpdates(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Chapter 5: Flatpak Application Updates
Update Flatpak applications which run in their own secure space.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner, checkCommandExists
import subprocess


def updateFlatpakApps(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Update Flatpak applications."""
    reporter.writeChapterHeader(5, "Updating Desktop Applications (Flatpak)")
    
    reporter.say("\n📱 Flatpak apps are like phone apps - they run in their" +
                " own secure space and update independently.")
    
    chapter_success = True
    
    if not checkCommandExists("flatpak"):
        reporter.say("Flatpak isn't installed. It's a great way to get the" +
                    " latest versions of apps like Spotify, Discord, etc.")
        reporter.setChapterStatus(5, True, "Not installed (optional)")
        return True
    
    # Check if any remotes are configured
    remote_count = checkFlatpakRemotes()
    
    if remote_count == 0:
        reporter.say("Flatpak is installed but not set up yet.", is_error=True)
        reporter.say("You can add the Flathub store with:")
        reporter.say("flatpak remote-add --if-not-exists flathub" +
                    " https://flathub.org/repo/flathub.flatpakrepo")
        reporter.setChapterStatus(5, False, "Not configured")
        return False
    
    reporter.say("\n🔄 Updating your Flatpak applications...")
    
    # Count installed apps
    app_count = countFlatpakApps()
    reporter.say("You have " + str(app_count) + " Flatpak apps installed.")
    
    # Update apps
    success, _ = runner.run(
        "update all Flatpak apps",
        ["flatpak", "update", "-y"]
    )
    if not success:
        chapter_success = False
    
    # Remove unused data
    success, _ = runner.run(
        "remove unused Flatpak data",
        ["flatpak", "uninstall", "--unused", "-y"]
    )
    if not success:
        chapter_success = False
    
    notes = str(app_count) + " apps updated"
    reporter.setChapterStatus(5, chapter_success, notes)
    return chapter_success


def checkFlatpakRemotes() -> int:
    """Check how many Flatpak remotes are configured."""
    try:
        result = subprocess.run(
            ["flatpak", "remote-list"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            lines = [line for line in result.stdout.strip().split('\n') if line]
            return len(lines)
        return 0
    except:
        return 0


def countFlatpakApps() -> int:
    """Count installed Flatpak applications."""
    try:
        result = subprocess.run(
            ["flatpak", "list", "--app"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            lines = [line for line in result.stdout.strip().split('\n') if line]
            return len(lines)
        return 0
    except:
        return 0


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = updateFlatpakApps(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

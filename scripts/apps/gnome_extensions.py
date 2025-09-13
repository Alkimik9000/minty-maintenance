#!/usr/bin/env python3
"""
Chapter 13: GNOME Extensions Update
Update GNOME Shell extensions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner, checkCommandExists
import subprocess


def updateGnomeExtensions(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Update GNOME extensions."""
    reporter.writeChapterHeader(13, "Updating Desktop Extensions")
    
    reporter.say("\n🧩 GNOME extensions customize your desktop experience." +
                " Let me check for updates...")
    
    chapter_success = True
    
    if not checkCommandExists("gnome-extensions"):
        reporter.say("GNOME extensions system not found. You can install" +
                    " Extension Manager from Software Center for easy management.")
        reporter.setChapterStatus(13, True, "Not available")
        return True
    
    # Count enabled extensions
    enabled_count = countEnabledExtensions()
    
    if enabled_count > 0:
        reporter.say("You have " + str(enabled_count) + " extensions enabled.")
        
        success, _ = runner.run(
            "update GNOME extensions",
            ["gnome-extensions", "update"]
        )
        if not success:
            chapter_success = False
        
        reporter.say("\n💡 For more control, use the Extension Manager app" +
                    " from Software Center.")
        reporter.setChapterStatus(13, chapter_success, 
                                str(enabled_count) + " extensions updated")
    else:
        reporter.say("No extensions are currently enabled.")
        reporter.setChapterStatus(13, True, "No extensions enabled")
    
    return chapter_success


def countEnabledExtensions() -> int:
    """Count how many GNOME extensions are enabled."""
    try:
        result = subprocess.run(
            ["gnome-extensions", "list", "--enabled"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            # Count non-empty lines
            lines = [line for line in result.stdout.strip().split('\n') if line]
            return len(lines)
        return 0
    except:
        return 0


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = updateGnomeExtensions(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

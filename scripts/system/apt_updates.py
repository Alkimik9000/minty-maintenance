#!/usr/bin/env python3
"""
Chapter 3: APT System Updates
Updates core system software including security fixes and bug repairs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner
from typing import Tuple
import subprocess


def performAptUpdates(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Perform APT system updates and cleanup."""
    reporter.writeChapterHeader(3, "Updating Your Core System Software")
    
    reporter.say("\n📦 Now for the important part - updating your system's" +
                " core software. This includes security fixes and bug repairs.")
    reporter.say("\nThis is like getting oil changes for your car - it keeps" +
                " everything running smoothly and safely.")
    
    chapter_success = True
    
    # Pre-update space check
    space_before_apt = reporter.getDiskSpace()
    
    # Refresh package list
    success, _ = runner.run(
        "refresh the list of available updates",
        ["sudo", "apt", "update"]
    )
    if not success:
        chapter_success = False
    
    # Check for broken packages
    reporter.say("\n🔧 Let me make sure nothing is broken before we start...")
    success, output = runner.run(
        "check and fix broken packages",
        ["sudo", "apt", "-f", "install", "-y"],
        check=False
    )
    if output and "0 upgraded" not in output:
        reporter.say("I fixed some package issues for you!")
    
    # Check what needs updating
    reporter.say("\n📋 Checking what needs updating...")
    update_count = checkAvailableUpdates(reporter)
    
    if update_count > 0:
        reporter.say("I found " + str(update_count) + " updates available.")
        
        if not reporter.isDryRun():
            # Run the upgrade
            success, output = runner.run(
                "install all system updates",
                ["sudo", "apt", "-o", "APT::Get::Always-Include-Phased-Updates=true",
                 "--allow-downgrades", "full-upgrade", "-y"]
            )
            if not success:
                reporter.say("Some packages couldn't be upgraded.", is_error=True)
                reporter.say("This is usually fine - they'll update later.")
                chapter_success = False
            else:
                reporter.say("✅ All updates installed successfully!")
        else:
            reporter.say("(Test mode: I would install these updates now)")
    else:
        reporter.say("Great news! Your system is already up to date.")
    
    # Cleanup
    reporter.say("\n🧹 Now let me clean up old stuff you don't need...")
    success, _ = runner.run(
        "remove packages that are no longer needed",
        ["sudo", "apt", "autoremove", "--purge", "-y"]
    )
    if not success:
        chapter_success = False
    
    success, _ = runner.run(
        "clean up the package download cache",
        ["sudo", "apt", "clean"]
    )
    if not success:
        chapter_success = False
    
    # Calculate space saved
    space_after_apt = reporter.getDiskSpace()
    space_saved = reporter.calculateSpaceDiff(space_before_apt, space_after_apt)
    
    if space_saved > 0:
        notes = "Updated & freed " + str(space_saved) + "MB"
        reporter.space_changes[3] = space_saved
    else:
        notes = "Updated successfully"
    
    reporter.setChapterStatus(3, chapter_success, notes)
    return chapter_success


def checkAvailableUpdates(reporter: MaintenanceReporter) -> int:
    """Check how many updates are available."""
    try:
        result = subprocess.run(
            ["apt", "list", "--upgradable"],
            capture_output=True,
            text=True,
            check=False
        )
        
        lines = result.stdout.strip().split('\n')
        # Filter out the "Listing..." line and count actual packages
        update_lines = [line for line in lines if line and "upgradable" in line]
        
        # Show first few updates
        if update_lines:
            reporter.say("Here are some highlights:")
            for line in update_lines[:5]:
                reporter.say("   " + line)
        
        return len(update_lines)
    except:
        return 0


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = performAptUpdates(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

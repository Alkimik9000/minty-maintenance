#!/usr/bin/env python3
"""
Chapter 9: Firmware Updates
Check and install device firmware updates.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner, checkCommandExists
import subprocess


def updateFirmware(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Check and install firmware updates."""
    reporter.writeChapterHeader(9, "Checking Device Firmware Updates")
    
    reporter.say("\n🔧 Firmware is the low-level software that runs your" +
                " hardware devices. Let me check if any updates are available...")
    
    chapter_success = True
    
    if not checkCommandExists("fwupdmgr"):
        reporter.say("Firmware updater not installed. Install it with:", is_error=True)
        reporter.say("sudo apt install fwupd")
        reporter.setChapterStatus(9, False, "fwupd not installed")
        return False
    
    reporter.say("\nThis might find updates for:")
    reporter.say("   • Your computer's BIOS/UEFI")
    reporter.say("   • SSD/hard drive firmware")
    reporter.say("   • Thunderbolt controllers")
    reporter.say("   • Other hardware components")
    
    # Refresh firmware metadata
    success, _ = runner.run(
        "refresh firmware update list",
        ["fwupdmgr", "refresh"],
        check=False
    )
    if not success:
        chapter_success = False
    
    # Check for updates
    reporter.say("\n🔍 Checking what firmware updates are available...")
    
    if reporter.isDryRun():
        reporter.say("(Test mode: Would check for firmware updates)")
        reporter.setChapterStatus(9, True, "No updates needed")
        return True
    
    # Check if updates are available
    result = subprocess.run(
        ["fwupdmgr", "get-updates"],
        capture_output=True,
        text=True,
        check=False
    )
    
    if result.returncode == 0:
        # Updates available
        reporter.say("\n⚠️ Firmware updates found! These are important" +
                    " for stability and security.")
        
        # Show update details
        if result.stdout:
            reporter.say(result.stdout)
        
        # Install updates
        success, _ = runner.run(
            "install firmware updates",
            ["fwupdmgr", "update"],
            check=False
        )
        if not success:
            chapter_success = False
        
        reporter.say("\n⚠️ IMPORTANT: You may need to restart your" +
                    " computer for firmware updates to complete!")
        reporter.setChapterStatus(9, chapter_success, "Updates installed - restart needed")
    else:
        # No updates or error
        if "No updates available" in result.stderr:
            reporter.say("✅ All firmware is up to date!")
            reporter.setChapterStatus(9, True, "All up to date")
        else:
            reporter.say("Could not check for firmware updates.", is_error=True)
            if result.stderr:
                reporter.say("Error: " + result.stderr[:200])
            reporter.setChapterStatus(9, False, "Check failed")
            chapter_success = False
    
    return chapter_success


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = updateFirmware(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Chapter 6: Snap Application Updates
Update Snap packages and clean up old revisions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner, checkCommandExists
import subprocess


def updateSnapApps(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Update Snap applications and clean old versions."""
    reporter.writeChapterHeader(6, "Updating Snap Applications")
    
    reporter.say("\n📦 Snap is another app system, similar to Flatpak." +
                " Let me check for updates and clean up old versions...")
    
    chapter_success = True
    
    if not checkCommandExists("snap"):
        reporter.say("Snap isn't installed. That's fine - Flatpak is usually" +
                    " preferred anyway.")
        reporter.setChapterStatus(6, True, "Not installed (optional)")
        return True
    
    # Check current retain setting
    current_retain = getSnapRetainSetting()
    reporter.say("Snap keeps old versions of apps as backups. I'll limit" +
                " this to save space.")
    
    if current_retain != "2":
        success, _ = runner.run(
            "set Snap to keep only 2 old versions",
            ["sudo", "snap", "set", "system", "refresh.retain=2"]
        )
        if not success:
            chapter_success = False
    
    # Update snaps
    success, _ = runner.run(
        "update all Snap applications",
        ["sudo", "snap", "refresh"]
    )
    if not success:
        chapter_success = False
    
    # Clean up old revisions
    reporter.say("\n🧹 Removing old app versions to free up space...")
    old_snaps = getOldSnapRevisions()
    
    if old_snaps:
        for snap_name, revision in old_snaps:
            if snap_name and revision:
                if not reporter.isDryRun():
                    success, output = runner.run(
                        "remove old version: " + snap_name + " (revision " + revision + ")",
                        ["sudo", "snap", "remove", snap_name, "--revision=" + revision],
                        check=False
                    )
                else:
                    reporter.say("Would remove old version: " + snap_name + 
                               " (revision " + revision + ")")
        
        reporter.setChapterStatus(6, chapter_success, "Updated & cleaned old versions")
    else:
        reporter.say("✅ No old versions to clean up.")
        reporter.setChapterStatus(6, chapter_success, "Updated, already clean")
    
    return chapter_success


def getSnapRetainSetting() -> str:
    """Get the current snap retain setting."""
    try:
        result = subprocess.run(
            ["snap", "get", "system", "refresh.retain"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            return result.stdout.strip()
        return "default"
    except:
        return "default"


def getOldSnapRevisions() -> list:
    """Get list of old snap revisions that can be removed."""
    try:
        result = subprocess.run(
            ["snap", "list", "--all"],
            capture_output=True,
            text=True,
            check=False
        )
        
        old_snaps = []
        if result.stdout:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                if 'disabled' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        snap_name = parts[0]
                        revision = parts[2]
                        old_snaps.append((snap_name, revision))
        
        return old_snaps
    except:
        return []


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = updateSnapApps(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

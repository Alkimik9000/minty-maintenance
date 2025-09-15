#!/usr/bin/env python3
"""
Chapter 4: Package Sanity Checks
Check for held packages and orphaned packages that take up space.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner, checkCommandExists
import subprocess


def checkPackageSanity(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Check for package issues like held packages and orphans."""
    reporter.writeChapterHeader(4, "Checking for Package Issues")
    
    reporter.say("\n🔍 Let me check if any software is being held back or" +
                " if there are any orphaned packages taking up space...")
    
    chapter_success = True
    
    # Check for held packages
    held_packages = checkHeldPackages(reporter)
    if held_packages:
        reporter.say("These packages are being held back from updates:", is_error=True)
        for pkg in held_packages[:10]:  # Show max 10
            reporter.say("   " + pkg)
        reporter.say("This might be intentional, but if you don't know why" +
                    " they're held, you might want to investigate.")
        notes = "Found held packages"
    else:
        reporter.say("✅ No packages are being held back. Good!")
        notes = "No issues found"
    
    # Check for orphaned packages
    if not checkCommandExists("deborphan"):
        success, _ = runner.run(
            "install tool to find orphaned packages",
            ["sudo", "apt", "install", "-y", "deborphan"],
            check=False
        )
    
    if checkCommandExists("deborphan"):
        orphans = checkOrphanedPackages(reporter)
        if orphans:
            orphan_count = len(orphans)
            reporter.say("\n🧹 Found " + str(orphan_count) + " orphaned packages that" +
                        " aren't needed anymore:")
            for pkg in orphans[:5]:
                reporter.say("   " + pkg)
            
            if not reporter.isDryRun():
                reporter.say("\nRemoving orphaned packages...")
                removed_count = 0
                for pkg in orphans:
                    if pkg.strip():
                        success, _ = runner.run(
                            "remove orphaned package: " + pkg,
                            ["sudo", "apt", "remove", "-y", pkg],
                            check=False
                        )
                        if success:
                            removed_count += 1
                        else:
                            chapter_success = False
                
                notes = "Cleaned " + str(removed_count) + " orphans"
            else:
                notes = "Found " + str(orphan_count) + " orphans"
        else:
            reporter.say("✅ No orphaned packages found. Your system is tidy!")
            if held_packages:
                notes = "Found held packages"
            else:
                notes = "No issues found"
    
    reporter.setChapterStatus(4, chapter_success, notes)
    return chapter_success


def checkHeldPackages(reporter: MaintenanceReporter) -> list:
    """Check for packages on hold."""
    try:
        result = subprocess.run(
            ["apt-mark", "showhold"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            return [line.strip() for line in result.stdout.strip().split('\n') if line]
        return []
    except:
        return []


def checkOrphanedPackages(reporter: MaintenanceReporter) -> list:
    """Check for orphaned packages using deborphan."""
    try:
        result = subprocess.run(
            ["deborphan"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            return [line.strip() for line in result.stdout.strip().split('\n') if line]
        return []
    except:
        return []


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = checkPackageSanity(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

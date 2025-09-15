#!/usr/bin/env python3
"""
Chapter 16: Deep Clean
Perform deep cleaning with BleachBit.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner, checkCommandExists
import subprocess


def performDeepClean(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Perform deep cleaning with BleachBit."""
    reporter.writeChapterHeader(16, "Deep Cleaning Temporary Files")
    
    reporter.say("\n🧹 BleachBit is like CCleaner for Linux - it removes" +
                " temporary files, caches, and other junk.")
    
    chapter_success = True
    
    if not checkCommandExists("bleachbit"):
        reporter.say("BleachBit is not installed. It's a great tool for" +
                    " freeing up disk space!")
        reporter.say("Install it from Software Center or with:" +
                    " sudo apt install bleachbit")
        reporter.setChapterStatus(16, True, "Not installed (optional)")
        return True
    
    reporter.say("\nThis will clean things like:")
    reporter.say("   • Web browser caches")
    reporter.say("   • Temporary files")
    reporter.say("   • Old logs")
    reporter.say("   • Thumbnail caches")
    
    # List available cleaners
    reporter.say("\n📋 Available cleaning options:")
    listCleaners(reporter)
    
    # Clean common safe items
    success, _ = runner.run(
        "perform deep clean (browser cache, temp files, logs)",
        ["bleachbit", "--clean", "system.cache", "system.tmp"],
        check=False
    )
    if not success:
        chapter_success = False
    
    reporter.say("\n💡 Run BleachBit (GUI) to customize what gets cleaned.")
    reporter.setChapterStatus(16, chapter_success, "Deep cleaned")
    return chapter_success


def listCleaners(reporter: MaintenanceReporter) -> None:
    """List available BleachBit cleaners."""
    try:
        result = subprocess.run(
            ["bleachbit", "--list-cleaners"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            # Show first 10 cleaners
            lines = result.stdout.strip().split('\n')[:10]
            for line in lines:
                reporter.say("   " + line)
    except:
        pass


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = performDeepClean(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

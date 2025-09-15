#!/usr/bin/env python3
"""
Chapter 10: Log Cleanup
Clean up old system log files to free up space.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner
import subprocess
import re


def cleanupLogs(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Clean up old system logs."""
    reporter.writeChapterHeader(10, "Cleaning Up System Log Files")
    
    reporter.say("\n📚 Your system keeps detailed logs of everything it does." +
                " Over time, these can take up quite a bit of space.")
    reporter.say("\nLet me clean up logs older than 2 weeks...")
    
    chapter_success = True
    
    # Check current journal size
    journal_size = getJournalSize()
    reporter.say("Current log storage: " + journal_size)
    
    # Clean up logs
    success, _ = runner.run(
        "clean up old system logs (keep 2 weeks)",
        ["sudo", "journalctl", "--vacuum-time=2weeks", "--vacuum-size=500M"]
    )
    if not success:
        chapter_success = False
    
    # Check new size
    new_journal_size = getJournalSize()
    reporter.say("Log storage after cleanup: " + new_journal_size)
    
    reporter.setChapterStatus(10, chapter_success, "Cleaned to " + new_journal_size)
    return chapter_success


def getJournalSize() -> str:
    """Get the current size of system journal logs."""
    try:
        result = subprocess.run(
            ["journalctl", "--disk-usage"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            # Extract size from output
            match = re.search(r'(\d+\.?\d*[MG])', result.stdout)
            if match:
                return match.group(1)
        
        return "unknown"
    except:
        return "unknown"


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = cleanupLogs(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

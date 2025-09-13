#!/usr/bin/env python3
"""
Chapter 15: Search Database Update
Refresh the file search database for the locate command.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner, checkCommandExists
import time


def updateSearchDatabase(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Update the file search database."""
    reporter.writeChapterHeader(15, "Refreshing File Search Database")
    
    reporter.say("\n🔍 Your system maintains a database of all files for" +
                " quick searching. Let me update it...")
    reporter.say("\nThis helps the 'locate' command find files instantly.")
    
    chapter_success = True
    
    # Check if database is recent
    db_file = "/var/lib/mlocate/mlocate.db"
    if os.path.exists(db_file):
        db_age_hours = getDatabaseAge(db_file)
        
        if db_age_hours < 24:
            reporter.say("✅ Database was updated " + str(db_age_hours) + 
                        " hours ago. Still fresh!")
            reporter.setChapterStatus(15, True, "Already up to date")
            return True
        else:
            reporter.say("Database is " + str(db_age_hours) + 
                        " hours old. Updating...")
    
    # Install or update database
    if checkCommandExists("updatedb"):
        success, _ = runner.run(
            "scan all files and update search database",
            ["sudo", "updatedb"]
        )
        if not success:
            chapter_success = False
        reporter.setChapterStatus(15, chapter_success, "Database refreshed")
    else:
        # Install mlocate
        success, _ = runner.run(
            "install file search tools",
            ["sudo", "apt", "install", "-y", "mlocate"]
        )
        if not success:
            chapter_success = False
            reporter.setChapterStatus(15, False, "Installation failed")
        else:
            success, _ = runner.run(
                "build initial database",
                ["sudo", "updatedb"]
            )
            if not success:
                chapter_success = False
            reporter.setChapterStatus(15, chapter_success, "Installed and initialized")
    
    reporter.say("\n⏱️ Note: This can take a while on large drives" +
                " with many files (like cloud storage folders).")
    
    return chapter_success


def getDatabaseAge(db_path: str) -> int:
    """Get the age of the database file in hours."""
    try:
        stat = os.stat(db_path)
        age_seconds = time.time() - stat.st_mtime
        return int(age_seconds / 3600)
    except:
        return 999  # Return large number if can't determine


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = updateSearchDatabase(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

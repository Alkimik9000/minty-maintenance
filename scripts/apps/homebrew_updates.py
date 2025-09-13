#!/usr/bin/env python3
"""
Chapter 2: Homebrew Updates
Update command-line tools managed by Homebrew.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner, checkCommandExists


def updateHomebrew(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Update Homebrew packages."""
    reporter.writeChapterHeader(2, "Updating Command-Line Tools (Homebrew)")
    
    reporter.say("\n🍺 Homebrew manages special command-line tools that" +
                " aren't in the regular software store.")
    
    chapter_success = True
    
    if not checkCommandExists("brew"):
        reporter.say("You don't have Homebrew installed. That's fine -" +
                    " you probably don't need it unless you're a developer.")
        reporter.setChapterStatus(2, True, "Not installed (optional)")
        return True
    
    reporter.say("\nLet me check for updates to your command-line tools...")
    
    # Update Homebrew itself
    success, _ = runner.run(
        "check for new versions",
        ["brew", "update"]
    )
    if not success:
        chapter_success = False
    
    # Upgrade packages
    success, _ = runner.run(
        "install the updates",
        ["brew", "upgrade"]
    )
    if not success:
        chapter_success = False
    
    reporter.setChapterStatus(2, chapter_success, "Tools updated")
    return chapter_success


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = updateHomebrew(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

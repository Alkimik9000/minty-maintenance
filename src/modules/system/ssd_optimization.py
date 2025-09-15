#!/usr/bin/env python3
"""
Chapter 17: SSD Optimization
Optimize SSD performance with TRIM.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner


def optimizeSSD(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Optimize SSD drives with TRIM."""
    reporter.writeChapterHeader(17, "Optimizing SSD Performance")
    
    reporter.say("\n⚡ If you have an SSD (solid-state drive), it needs" +
                " periodic optimization to maintain performance.")
    reporter.say("\nThis process is called 'trimming' and helps the drive" +
                " manage deleted data efficiently.")
    
    # Run fstrim on all mounted filesystems
    success, _ = runner.run(
        "optimize all SSD drives",
        ["sudo", "fstrim", "-av"]
    )
    
    reporter.say("\n📝 Note: You'll see errors for non-SSD drives or" +
                " filesystems that don't support trimming. This is normal!")
    
    reporter.say("\n💡 Your system should do this automatically weekly," +
                " but running it manually ensures it's done.")
    
    reporter.setChapterStatus(17, success, "SSDs optimized")
    return success


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = optimizeSSD(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

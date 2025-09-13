#!/usr/bin/env python3
"""
Chapter 12: Disk Health Check
Check hard drive health using SMART tools.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner, checkCommandExists
import subprocess


def checkDiskHealth(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Check health of storage drives."""
    reporter.writeChapterHeader(12, "Checking Hard Drive Health")
    
    reporter.say("\n💾 Let me check if your storage drives are healthy...")
    
    chapter_success = True
    
    # Install SMART tools if needed
    if not checkCommandExists("smartctl"):
        success, _ = runner.run(
            "install disk health monitoring tools",
            ["sudo", "apt", "install", "-y", "smartmontools"]
        )
        if not success:
            chapter_success = False
    
    if checkCommandExists("smartctl"):
        # Find all disk devices
        disks = findDiskDevices()
        
        if disks:
            reporter.say("\nChecking " + str(len(disks)) + " storage device(s)...")
            
            all_healthy = True
            for disk in disks:
                # Skip zram devices (compressed RAM, not physical disks)
                if disk.startswith("zram"):
                    continue
                
                reporter.say("\n📊 Checking /dev/" + disk + "...")
                
                # Check disk health
                result = subprocess.run(
                    ["sudo", "smartctl", "-H", "/dev/" + disk],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.stdout and "PASSED" in result.stdout:
                    reporter.say("   ✅ Healthy!")
                else:
                    reporter.say("   ⚠️ This drive may have issues!" +
                               " Consider backing up important data.", is_error=True)
                    all_healthy = False
                    chapter_success = False
            
            if all_healthy:
                reporter.setChapterStatus(12, True, "All drives healthy")
            else:
                reporter.setChapterStatus(12, False, "Drive issues detected!")
            
            reporter.say("\n💡 Tip: For a thorough test, run:" +
                        " sudo smartctl -t long /dev/sdX")
            reporter.say("   (Replace sdX with your drive name)")
        else:
            reporter.say("No disk devices found to check.")
            reporter.setChapterStatus(12, True, "No disks found")
    else:
        reporter.say("Could not check disk health.", is_error=True)
        reporter.setChapterStatus(12, False, "Tools not available")
        chapter_success = False
    
    return chapter_success


def findDiskDevices() -> list:
    """Find all disk devices in the system."""
    try:
        result = subprocess.run(
            ["lsblk", "-ndo", "TYPE,NAME"],
            capture_output=True,
            text=True,
            check=False
        )
        
        disks = []
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                parts = line.split()
                if len(parts) >= 2 and parts[0] == "disk":
                    disks.append(parts[1])
        
        return disks
    except:
        return []


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = checkDiskHealth(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

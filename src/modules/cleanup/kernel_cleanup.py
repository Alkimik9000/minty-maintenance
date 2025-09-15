#!/usr/bin/env python3
"""
Chapter 11: Kernel Cleanup
Remove old system kernels, keeping the newest ones.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner, checkCommandExists
import subprocess
import re


def cleanupKernels(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Clean up old kernel versions."""
    reporter.writeChapterHeader(11, "Removing Old System Kernels")
    
    reporter.say("\n🖥️ The kernel is the core of your operating system." +
                " When it updates, old versions are kept as backups.")
    reporter.say("\nLet me clean up old kernels, keeping the newest 2...")
    
    chapter_success = True
    
    # Install tool if needed
    if not checkCommandExists("purge-old-kernels"):
        success, _ = runner.run(
            "install kernel cleanup tool",
            ["sudo", "apt", "install", "-y", "byobu"]
        )
        if not success:
            chapter_success = False
    
    # Check current kernels
    kernel_count = countInstalledKernels()
    reporter.say("You currently have " + str(kernel_count) + " kernels installed.")
    
    if kernel_count > 2:
        # Check for held kernels
        held_kernels = checkHeldKernels()
        if held_kernels:
            reporter.say("These kernels are being held:", is_error=True)
            for kernel in held_kernels:
                reporter.say("   " + kernel)
        
        # Remove old kernels
        success, _ = runner.run(
            "remove old kernels (keeping newest 2)",
            ["sudo", "purge-old-kernels", "-y", "2"]
        )
        if not success:
            chapter_success = False
        
        reporter.setChapterStatus(11, chapter_success, "Cleaned old kernels")
    else:
        reporter.say("✅ You only have " + str(kernel_count) + 
                    " kernels. No cleanup needed!")
        reporter.setChapterStatus(11, True, "Already clean")
    
    return chapter_success


def countInstalledKernels() -> int:
    """Count how many kernels are installed."""
    try:
        result = subprocess.run(
            ["dpkg", "-l"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            # Count lines that match kernel package pattern
            kernel_pattern = re.compile(r'^ii\s+linux-image-\d')
            count = 0
            for line in result.stdout.split('\n'):
                if kernel_pattern.match(line):
                    count += 1
            return count
        return 0
    except:
        return 0


def checkHeldKernels() -> list:
    """Check for kernels that are being held."""
    try:
        result = subprocess.run(
            ["apt-mark", "showhold"],
            capture_output=True,
            text=True,
            check=False
        )
        
        held_kernels = []
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if 'linux-image' in line:
                    held_kernels.append(line.strip())
        
        return held_kernels
    except:
        return []


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = cleanupKernels(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

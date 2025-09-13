#!/usr/bin/env python3
"""
Chapter 19: Graphics Card Check
Check NVIDIA graphics card status and health.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner, checkCommandExists
import subprocess
import re


def checkGraphicsCard(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Check NVIDIA graphics card status."""
    reporter.writeChapterHeader(19, "Checking Graphics Card Status")
    
    reporter.say("\n🎮 You have an NVIDIA GTX 1080 graphics card." +
                " Let me check its status...")
    
    chapter_success = True
    
    if not checkCommandExists("nvidia-smi"):
        reporter.say("NVIDIA drivers don't seem to be properly installed.", is_error=True)
        reporter.say("Your graphics might be using basic drivers.")
        reporter.setChapterStatus(19, False, "NVIDIA tools not found")
        return False
    
    # Get GPU info
    gpu_info = getGPUInfo()
    
    if gpu_info:
        driver, gpu_name, memory, temp = gpu_info
        
        reporter.say("\n✅ Graphics card detected!")
        reporter.say("   • Card: " + gpu_name)
        reporter.say("   • Driver: " + driver)
        reporter.say("   • Memory: " + memory)
        reporter.say("   • Temperature: " + str(temp) + "°C")
        
        # Check temperature
        if temp > 80:
            reporter.say("⚠️ Your GPU is running hot! Check for dust" +
                        " in the fans or improve case ventilation.", is_error=True)
        
        reporter.setChapterStatus(19, True, "GPU healthy, driver " + driver)
    else:
        reporter.say("Could not read GPU information.", is_error=True)
        reporter.setChapterStatus(19, False, "GPU detection issue")
        chapter_success = False
    
    return chapter_success


def getGPUInfo() -> tuple:
    """Get NVIDIA GPU information."""
    try:
        result = subprocess.run(
            ["nvidia-smi", 
             "--query-gpu=driver_version,name,memory.total,temperature.gpu",
             "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            # Parse CSV output
            parts = result.stdout.strip().split(', ')
            if len(parts) >= 4:
                driver = parts[0]
                gpu_name = parts[1]
                memory = parts[2]
                temp_str = parts[3]
                
                # Extract temperature number
                temp_match = re.match(r'(\d+)', temp_str)
                temp = int(temp_match.group(1)) if temp_match else 0
                
                return (driver, gpu_name, memory, temp)
        
        return None
    except:
        return None


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = checkGraphicsCard(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

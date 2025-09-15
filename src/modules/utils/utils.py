#!/usr/bin/env python3
"""
Common utility functions for the Mint Maintenance scripts.
Following coding standards:
- Functions use camelCase
- Variables use snake_case
- Full type annotations
- No f-strings (using concatenation/format for Python compatibility)
"""

import os
import sys
import subprocess
import datetime
from typing import Dict, Optional, Tuple, List, Any
import json
import tempfile
import shutil


class MaintenanceReporter:
    """Handles report generation and management for system maintenance."""
    
    def __init__(self, report_dir: str = None, dry_run: bool = None):
        """Initialize reporter with optional report directory."""
        self.report_dir = report_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
        self.user_report_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'Reports', 'Minty-Maintenance')
        os.makedirs(self.user_report_dir, exist_ok=True)
        self._dry_run = dry_run  # Store dry_run flag if provided
        
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.report_path = os.path.join(
            self.report_dir, 
            "system-maintenance-report-" + self.timestamp + ".txt"
        )
        self.user_report_path = os.path.join(
            self.user_report_dir, 
            "system-maintenance-report-" + self.timestamp + ".txt"
        )
        self.chapter_status: Dict[int, str] = {}
        self.chapter_notes: Dict[int, str] = {}
        self.space_changes: Dict[int, int] = {}
        self.initial_space = self.getDiskSpace()
        
        # Ensure report directory exists
        os.makedirs(self.report_dir, exist_ok=True)
        
    def getDiskSpace(self) -> str:
        """Get available disk space on root partition."""
        try:
            result = subprocess.run(
                ["df", "-h", "/"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                # Extract available space (4th column)
                return lines[1].split()[3]
        except Exception:
            pass
        return "Unknown"
    
    def calculateSpaceDiff(self, before: str, after: str) -> int:
        """Calculate difference between two human-readable space values."""
        def parseSize(size_str: str) -> float:
            """Convert human-readable size to MB."""
            size_str = size_str.strip()
            if not size_str or size_str == "Unknown":
                return 0.0
                
            # Extract number and unit
            import re
            match = re.match(r'([\d.]+)([KMGT]?)', size_str)
            if not match:
                return 0.0
                
            number = float(match.group(1))
            unit = match.group(2)
            
            # Convert to MB
            multipliers = {'K': 1/1024, 'M': 1, 'G': 1024, 'T': 1024*1024}
            return number * multipliers.get(unit, 1)
        
        before_mb = parseSize(before)
        after_mb = parseSize(after)
        return int(after_mb - before_mb)
    
    def writeHeader(self) -> None:
        """Write report header with system info."""
        header_text = """🖥️  SYSTEM MAINTENANCE REPORT
============================

Hello! I'm your computer maintenance assistant.
Today is {date}

I'm going to help keep your computer running smoothly by:
• Installing security updates
• Cleaning up unnecessary files
• Checking your system's health
• Making sure everything is up-to-date

Mode: {mode}
Your system: Linux Mint 22 with GNOME desktop
This report: {report}

📑 What I'll Do Today:
----------------------
1. Create a Safety Checkpoint
2. Update Command-Line Tools (Homebrew)
3. Update System Software (APT)
4. Check for Package Issues
5. Update Desktop Applications (Flatpak)
6. Update Snap Applications
7. Update Python Tools
8. Check Standalone Applications
9. Update Device Firmware
10. Clean Up Old Log Files
11. Remove Old System Kernels
12. Check Hard Drive Health
13. Update Desktop Extensions
14. Clean Up Docker Containers
15. Refresh File Search Database
16. Deep Clean Temporary Files
17. Optimize SSD Performance
18. Check System Health
19. Check Graphics Card
20. Verify Automatic Updates
21. Final Summary

Let's begin! This usually takes 10-30 minutes.

""".format(
            date=datetime.datetime.now().strftime('%A, %B %d, %Y at %I:%M %p'),
            mode='Test Run (no changes will be made)' if self.isDryRun() else 'Full Maintenance',
            report=self.report_path
        )
        
        with open(self.report_path, 'w') as f:
            f.write(header_text)
        
        with open(self.user_report_path, 'w') as f:
            f.write(header_text)
    
    def say(self, message: str, is_error: bool = False) -> None:
        """Write message to both console and report."""
        prefix = "⚠️  " if is_error else ""
        full_message = prefix + message
        
        # Console output
        print(full_message)
        
        # Report output
        with open(self.report_path, 'a') as f:
            f.write(full_message + '\n')
        
        with open(self.user_report_path, 'a') as f:
            f.write(full_message + '\n')
    
    def writeChapterHeader(self, chapter_num: int, title: str) -> None:
        """Write a chapter header."""
        header = """
# ------------------------------------------------------------
# Chapter {} — {}
# ------------------------------------------------------------

""".format(chapter_num, title)
        
        print(header)
        with open(self.report_path, 'a') as f:
            f.write(header)
        
        with open(self.user_report_path, 'a') as f:
            f.write(header)
    
    def setChapterStatus(self, chapter_num: int, success: bool, notes: str = "") -> None:
        """Set the status for a chapter."""
        if success:
            self.chapter_status[chapter_num] = "✅ Success"
        else:
            self.chapter_status[chapter_num] = "⚠️ Needs Attention"
        
        if notes:
            self.chapter_notes[chapter_num] = notes
    
    def writeFinalSummary(self) -> None:
        """Write the final summary table."""
        final_space = self.getDiskSpace()
        total_space_change = self.calculateSpaceDiff(self.initial_space, final_space)
        
        self.say("\n🎉 All done! Here's what happened today:")
        self.say("")
        
        # Chapter names
        chapter_names = {
            1: "Safety Checkpoint",
            2: "Homebrew Tools",
            3: "System Updates",
            4: "Package Cleanup",
            5: "Flatpak Apps",
            6: "Snap Apps",
            7: "Python Tools",
            8: "AppImage Check",
            9: "Firmware Updates",
            10: "Log Cleanup",
            11: "Kernel Cleanup",
            12: "Disk Health",
            13: "GNOME Extensions",
            14: "Docker Cleanup",
            15: "Search Database",
            16: "Deep Clean",
            17: "SSD Optimization",
            18: "System Health",
            19: "Graphics Card",
            20: "Auto Updates"
        }
        
        # Write summary table
        self.say("\n{:<30} | {:<20} | {:<30}".format("Task", "Status", "Notes"))
        self.say("{:<30} | {:<20} | {:<30}".format("-"*30, "-"*20, "-"*30))
        
        for i in range(1, 21):
            task = chapter_names.get(i, "Unknown")
            status = self.chapter_status.get(i, "Unknown")
            notes = self.chapter_notes.get(i, "No data")
            self.say("{:<30} | {:<20} | {:<30}".format(task, status, notes))
        
        # Space summary
        self.say("\n📊 Space Summary:")
        if total_space_change > 0:
            self.say("   🎉 Freed up approximately " + str(total_space_change) + "MB!")
        elif total_space_change < -100:
            self.say("   📈 Used " + str(abs(total_space_change)) + "MB (updates need space)")
        else:
            self.say("   ↔️ Disk space remained about the same")
        self.say("   Available space: " + final_space)
        
        # Count issues
        issues = sum(1 for status in self.chapter_status.values() if "Attention" in status)
        
        self.say("\n📋 Overall Assessment:")
        if issues == 0:
            self.say("   🌟 Your system is in excellent shape!")
            self.say("   All maintenance tasks completed successfully.")
        elif issues <= 3:
            self.say("   👍 Your system is in good shape overall.")
            self.say("   A few minor items need attention when convenient.")
        else:
            self.say("   ⚠️ Several items need your attention.")
            self.say("   Review the orange items above for details.")
        
        # Check for reboot
        if os.path.exists("/var/run/reboot-required"):
            self.say("\n🔄 IMPORTANT: A restart is required!")
            self.say("   Some updates (like kernel or firmware) need a")
            self.say("   restart to take effect. Please restart soon.")
        
        self.say("\n💾 This report has been saved to:")
        self.say("   " + self.report_path)
        self.say("   " + self.user_report_path)
        
        self.say("\n🗓️ When to run maintenance again:")
        self.say("   • Weekly: For best performance and security")
        self.say("   • Monthly: Minimum recommended frequency")
        self.say("   • After major system changes or if issues arise")
        
        self.say("\n👋 Thank you for maintaining your system!")
        self.say("   Your computer appreciates the care!")
    
    def isDryRun(self) -> bool:
        """Check if running in dry-run mode."""
        if self._dry_run is not None:
            return self._dry_run
        return len(sys.argv) > 1 and sys.argv[1] == "dry-run"


class CommandRunner:
    """Handles command execution with friendly output."""
    
    def __init__(self, reporter: MaintenanceReporter):
        """Initialize with a reporter instance."""
        self.reporter = reporter
        self.dry_run = reporter.isDryRun()
    
    def run(self, description: str, command: List[str], 
            check: bool = True, capture_output: bool = True) -> Tuple[bool, str]:
        """
        Run a command with friendly description.
        Returns (success, output) tuple.
        """
        self.reporter.say("\n🔧 Now I'm going to: " + description)
        
        # Always show the actual command for debugging/logging
        self.reporter.say("   Command: " + " ".join(command))
        
        if self.dry_run:
            self.reporter.say("   (Test mode: Just checking what would happen)")
            return (True, "")
        
        # Capture space before operation
        space_before = self.reporter.getDiskSpace()
        
        try:
            if capture_output:
                # Show command execution in real time for better logging
                self.reporter.say("   Executing...")
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=check
                )
                output = result.stdout
                
                # Show all output if we're in verbose logging mode (when MINTY_TEE is set)
                if os.environ.get('MINTY_TEE'):
                    # Show complete output for logging
                    if output.strip():
                        self.reporter.say("   Output:")
                        for line in output.strip().split('\n'):
                            self.reporter.say("   > " + line)
                    if result.stderr and result.stderr.strip():
                        self.reporter.say("   Errors:")
                        for line in result.stderr.strip().split('\n'):
                            self.reporter.say("   ! " + line)
                else:
                    # Show only relevant output lines for interactive mode
                    if output:
                        important_lines = []
                        for line in output.split('\n'):
                            if any(word in line.lower() for word in 
                                   ['upgraded', 'removed', 'freed', 'installed', 'cleaned']):
                                important_lines.append(line)
                        
                        if important_lines:
                            for line in important_lines[:5]:
                                self.reporter.say("   " + line)
            else:
                result = subprocess.run(command, check=check)
                output = ""
            
            # Calculate space change
            space_after = self.reporter.getDiskSpace()
            space_diff = self.reporter.calculateSpaceDiff(space_before, space_after)
            
            if space_diff > 0:
                self.reporter.say("   ✅ Done! This freed up about " + 
                                str(space_diff) + "MB of space.")
            elif space_diff < 0:
                self.reporter.say("   ✅ Done! This used about " + 
                                str(abs(space_diff)) + "MB of space.")
            else:
                self.reporter.say("   ✅ Done! Everything completed successfully.")
            
            return (True, output)
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if hasattr(e, 'stderr') and e.stderr else str(e)
            self.analyzeError(error_msg)
            return (False, error_msg)
        except Exception as e:
            self.reporter.say("Something went wrong: " + str(e), is_error=True)
            return (False, str(e))
    
    def analyzeError(self, error_msg: str) -> None:
        """Analyze and explain errors in user-friendly terms."""
        self.reporter.say("Something didn't work as expected. Let me explain:", is_error=True)
        
        if "permission denied" in error_msg.lower():
            self.reporter.say("This needs administrator privileges. You might " +
                            "need to enter your password.", is_error=True)
        elif "not found" in error_msg.lower():
            self.reporter.say("The program I need isn't installed yet. This " +
                            "is normal - I'll try to install it for you.", is_error=True)
        elif "unable to lock" in error_msg.lower():
            self.reporter.say("Another update program is running. Please close " +
                            "Software Updater or Synaptic and try again.", is_error=True)
        elif "no space left" in error_msg.lower():
            self.reporter.say("Your disk is full! We need to free up space " +
                            "before continuing. Try emptying your trash.", is_error=True)
        else:
            self.reporter.say("Technical details: " + error_msg[:200], is_error=True)


def checkCommandExists(command: str) -> bool:
    """Check if a command exists in PATH."""
    return shutil.which(command) is not None


def getRealUserHome() -> str:
    """Get the real user's home directory (not root when using sudo)."""
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user:
        try:
            import pwd
            return pwd.getpwnam(sudo_user).pw_dir
        except:
            pass
    return os.path.expanduser("~")


def sendDesktopNotification(title: str, message: str) -> None:
    """Send a desktop notification if possible."""
    if checkCommandExists("notify-send"):
        try:
            subprocess.run(
                ["notify-send", title, message],
                check=False,
                capture_output=True
            )
        except:
            pass  # Silently ignore notification failures

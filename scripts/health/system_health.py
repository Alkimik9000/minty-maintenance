#!/usr/bin/env python3
"""
Chapter 18: System Health Check
Check overall system health including services and logs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner
import subprocess


def checkSystemHealth(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Check overall system health."""
    reporter.writeChapterHeader(18, "Checking Overall System Health")
    
    reporter.say("\n🏥 Let me run a quick health check on your system...")
    
    chapter_success = True
    
    # Check for failed services
    reporter.say("\n🔴 Checking for failed services...")
    failed_services = checkFailedServices()
    
    if not failed_services:
        reporter.say("✅ All system services are running properly!")
        notes = "All services healthy"
    else:
        reporter.say("Found some services with issues:", is_error=True)
        for service in failed_services[:10]:  # Show max 10
            reporter.say("   " + service)
        reporter.say("\nThese might need attention, but many are not critical.")
        notes = "Some service issues"
        chapter_success = False
    
    # Check for critical errors in logs
    reporter.say("\n📊 Checking system logs for critical issues...")
    critical_errors = checkCriticalErrors()
    
    if critical_errors:
        reporter.say("Found some system warnings (most are usually harmless):")
        for error in critical_errors[:5]:  # Show max 5
            reporter.say("   " + error)
    else:
        reporter.say("✅ No critical errors in recent logs!")
    
    reporter.setChapterStatus(18, chapter_success, notes)
    return chapter_success


def checkFailedServices() -> list:
    """Check for failed systemd services."""
    try:
        result = subprocess.run(
            ["systemctl", "--failed", "--no-pager", "--no-legend"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            return [line.strip() for line in result.stdout.strip().split('\n') if line]
        return []
    except:
        return []


def checkCriticalErrors() -> list:
    """Check for critical errors in system logs."""
    try:
        result = subprocess.run(
            ["journalctl", "-p", "3", "-xb", "--no-pager"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            # Get last 5 non-header lines
            lines = result.stdout.strip().split('\n')
            errors = []
            for line in reversed(lines):
                if not line.startswith('--') and line.strip():
                    errors.append(line.strip())
                    if len(errors) >= 5:
                        break
            return errors
        return []
    except:
        return []


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = checkSystemHealth(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

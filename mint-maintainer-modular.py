#!/usr/bin/env python3
"""
Linux Mint System Maintenance Script - Modular Version
Orchestrates individual maintenance tasks for Linux Mint 22.

Usage:
    python3 mint-maintainer-modular.py          # full run
    python3 mint-maintainer-modular.py dry-run  # simulate; no changes
"""

import sys
import os
import importlib.util
from typing import Dict, List, Tuple, Optional

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.utils.utils import (
    MaintenanceReporter, 
    CommandRunner, 
    sendDesktopNotification
)


class MaintenanceOrchestrator:
    """Orchestrates all maintenance chapters."""
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.reporter = MaintenanceReporter()
        self.runner = CommandRunner(self.reporter)
        self.chapters = self.loadChapters()
        
    def loadChapters(self) -> Dict[int, Dict[str, any]]:
        """Load all chapter modules."""
        chapters = {
            1: {
                'name': 'Safety Checkpoint',
                'module': 'scripts.system.timeshift_checkpoint',
                'function': 'createTimeshiftCheckpoint',
                'category': 'system'
            },
            2: {
                'name': 'Homebrew Updates',
                'module': 'scripts.apps.homebrew_updates',
                'function': 'updateHomebrew',
                'category': 'apps'
            },
            3: {
                'name': 'APT System Updates', 
                'module': 'scripts.system.apt_updates',
                'function': 'performAptUpdates',
                'category': 'system'
            },
            4: {
                'name': 'Package Sanity Checks',
                'module': 'scripts.system.package_sanity',
                'function': 'checkPackageSanity',
                'category': 'system'
            },
            5: {
                'name': 'Flatpak Applications',
                'module': 'scripts.apps.flatpak_updates',
                'function': 'updateFlatpakApps',
                'category': 'apps'
            },
            6: {
                'name': 'Snap Applications',
                'module': 'scripts.apps.snap_updates',
                'function': 'updateSnapApps',
                'category': 'apps'
            },
            7: {
                'name': 'Python Tools',
                'module': 'scripts.apps.python_updates',
                'function': 'updatePythonTools',
                'category': 'apps'
            },
            8: {
                'name': 'Standalone Applications Check',
                'module': 'scripts.apps.standalone_apps',
                'function': 'checkStandaloneApps',
                'category': 'apps'
            },
            9: {
                'name': 'Firmware Updates',
                'module': 'scripts.system.firmware_updates',
                'function': 'updateFirmware',
                'category': 'system'
            },
            10: {
                'name': 'Log Cleanup',
                'module': 'scripts.cleanup.log_cleanup',
                'function': 'cleanupLogs',
                'category': 'cleanup'
            },
            11: {
                'name': 'Kernel Cleanup',
                'module': 'scripts.cleanup.kernel_cleanup',
                'function': 'cleanupKernels',
                'category': 'cleanup'
            },
            12: {
                'name': 'Disk Health Check',
                'module': 'scripts.health.disk_health',
                'function': 'checkDiskHealth',
                'category': 'health'
            },
            13: {
                'name': 'GNOME Extensions',
                'module': 'scripts.apps.gnome_extensions',
                'function': 'updateGnomeExtensions',
                'category': 'apps'
            },
            14: {
                'name': 'Docker Cleanup',
                'module': 'scripts.cleanup.docker_cleanup',
                'function': 'cleanupDocker',
                'category': 'cleanup'
            },
            15: {
                'name': 'Search Database Update',
                'module': 'scripts.system.search_database',
                'function': 'updateSearchDatabase',
                'category': 'system'
            },
            16: {
                'name': 'Deep Clean',
                'module': 'scripts.cleanup.deep_clean',
                'function': 'performDeepClean',
                'category': 'cleanup'
            },
            17: {
                'name': 'SSD Optimization',
                'module': 'scripts.system.ssd_optimization',
                'function': 'optimizeSSD',
                'category': 'system'
            },
            18: {
                'name': 'System Health Check',
                'module': 'scripts.health.system_health',
                'function': 'checkSystemHealth',
                'category': 'health'
            },
            19: {
                'name': 'Graphics Card Check',
                'module': 'scripts.health.gpu_check',
                'function': 'checkGraphicsCard',
                'category': 'health'
            },
            20: {
                'name': 'Automatic Updates Check',
                'module': 'scripts.system.auto_updates',
                'function': 'checkAutoUpdates',
                'category': 'system'
            }
        }
        return chapters
    
    def runChapter(self, chapter_num: int, chapter_info: Dict) -> bool:
        """Run a single chapter."""
        try:
            # Check if module file exists
            module_path = chapter_info['module'].replace('.', '/') + '.py'
            if not os.path.exists(module_path):
                self.reporter.say("Chapter " + str(chapter_num) + " (" + 
                                chapter_info['name'] + ") not yet implemented")
                self.reporter.setChapterStatus(chapter_num, True, "Not implemented")
                return True
            
            # Import module dynamically
            module = importlib.import_module(chapter_info['module'])
            function = getattr(module, chapter_info['function'])
            
            # Run the chapter function
            success = function(self.reporter, self.runner)
            return success
            
        except Exception as e:
            self.reporter.say("Error running chapter " + str(chapter_num) + 
                            ": " + str(e), is_error=True)
            self.reporter.setChapterStatus(chapter_num, False, "Error: " + str(e)[:30])
            return False
    
    def run(self) -> None:
        """Run all maintenance tasks."""
        # Write report header
        self.reporter.writeHeader()
        
        # Run each chapter
        for chapter_num in sorted(self.chapters.keys()):
            chapter_info = self.chapters[chapter_num]
            self.runChapter(chapter_num, chapter_info)
        
        # Write final summary
        self.reporter.writeFinalSummary()
        
        # Send desktop notification
        issue_count = sum(1 for status in self.reporter.chapter_status.values() 
                         if "Attention" in status)
        
        if issue_count == 0:
            sendDesktopNotification(
                "✅ Maintenance Complete!",
                "All tasks successful. Report saved."
            )
        else:
            sendDesktopNotification(
                "⚠️ Maintenance Complete",
                str(issue_count) + " items need attention. Check report."
            )


def main() -> None:
    """Main entry point."""
    orchestrator = MaintenanceOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()

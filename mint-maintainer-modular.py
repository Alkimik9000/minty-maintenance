#!/usr/bin/env python3
"""
Linux Mint System Maintenance Script - Modular Version
Orchestrates individual maintenance tasks for Linux Mint 22.

Usage:
    python3 mint-maintainer-modular.py                    # full run
    python3 mint-maintainer-modular.py dry-run            # simulate; no changes
    python3 mint-maintainer-modular.py --manifest <file>  # run selected modules from manifest
"""

import sys
import os
import json
import argparse
import importlib.util
import subprocess
from typing import Dict, Optional

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.utils.utils import (
    MaintenanceReporter, 
    CommandRunner, 
    sendDesktopNotification
)


class MaintenanceOrchestrator:
    """Orchestrates all maintenance chapters."""
    
    def __init__(self, manifest_path: Optional[str] = None):
        """Initialize the orchestrator."""
        self.manifest = None
        self.dry_run = False
        self.selected_modules = []
        
        # Load manifest if provided
        if manifest_path:
            with open(manifest_path, 'r') as f:
                self.manifest = json.load(f)
                self.dry_run = self.manifest.get('dry_run', False)
                self.selected_modules = self.manifest.get('selected', [])
        
        self.reporter = MaintenanceReporter(dry_run=self.dry_run)
        self.runner = CommandRunner(self.reporter)
        self.chapters = self.loadChapters()
        self.module_id_map = self.createModuleIdMap()
        
    def loadChapters(self) -> Dict[int, Dict[str, any]]:
        """Load all chapter modules."""
        chapters = {
            1: {
                'name': 'Safety Checkpoint',
                'module': 'scripts.system.timeshift_checkpoint',
                'function': 'createTimeshiftCheckpoint',
                'category': 'system',
                'module_id': 'sys:timeshift'
            },
            2: {
                'name': 'Homebrew Updates',
                'module': 'scripts.apps.homebrew_updates',
                'function': 'updateHomebrew',
                'category': 'apps',
                'module_id': 'apps:check_brew'
            },
            3: {
                'name': 'APT System Updates', 
                'module': 'scripts.system.apt_updates',
                'function': 'performAptUpdates',
                'category': 'system',
                'module_id': 'sys:update_apt'
            },
            4: {
                'name': 'Package Sanity Checks',
                'module': 'scripts.system.package_sanity',
                'function': 'checkPackageSanity',
                'category': 'system',
                'module_id': 'clean:orphans'
            },
            5: {
                'name': 'Flatpak Applications',
                'module': 'scripts.apps.flatpak_updates',
                'function': 'updateFlatpakApps',
                'category': 'apps',
                'module_id': 'apps:update_flatpak'
            },
            6: {
                'name': 'Snap Applications',
                'module': 'scripts.apps.snap_updates',
                'function': 'updateSnapApps',
                'category': 'apps',
                'module_id': 'apps:update_snap'
            },
            7: {
                'name': 'Python Tools',
                'module': 'scripts.apps.python_updates',
                'function': 'updatePythonTools',
                'category': 'apps',
                'module_id': 'apps:update_python'
            },
            8: {
                'name': 'Standalone Applications Check',
                'module': 'scripts.apps.standalone_apps',
                'function': 'checkStandaloneApps',
                'category': 'apps',
                'module_id': 'apps:scan_standalone'
            },
            9: {
                'name': 'Firmware Updates',
                'module': 'scripts.system.firmware_updates',
                'function': 'updateFirmware',
                'category': 'system',
                'module_id': 'sys:update_firmware'
            },
            10: {
                'name': 'Log Cleanup',
                'module': 'scripts.cleanup.log_cleanup',
                'function': 'cleanupLogs',
                'category': 'cleanup',
                'module_id': 'clean:logs'
            },
            11: {
                'name': 'Kernel Cleanup',
                'module': 'scripts.cleanup.kernel_cleanup',
                'function': 'cleanupKernels',
                'category': 'cleanup',
                'module_id': 'sys:manage_kernels'
            },
            12: {
                'name': 'Disk Health Check',
                'module': 'scripts.health.disk_health',
                'function': 'checkDiskHealth',
                'category': 'health',
                'module_id': 'health:disk'
            },
            13: {
                'name': 'GNOME Extensions',
                'module': 'scripts.apps.gnome_extensions',
                'function': 'updateGnomeExtensions',
                'category': 'apps',
                'module_id': None  # Not in TUI
            },
            14: {
                'name': 'Docker Cleanup',
                'module': 'scripts.cleanup.docker_cleanup',
                'function': 'cleanupDocker',
                'category': 'cleanup',
                'module_id': 'clean:docker'
            },
            15: {
                'name': 'Search Database Update',
                'module': 'scripts.system.search_database',
                'function': 'updateSearchDatabase',
                'category': 'system',
                'module_id': 'clean:updatedb'
            },
            16: {
                'name': 'Deep Clean',
                'module': 'scripts.cleanup.deep_clean',
                'function': 'performDeepClean',
                'category': 'cleanup',
                'module_id': 'clean:bleachbit'
            },
            17: {
                'name': 'SSD Optimization',
                'module': 'scripts.system.ssd_optimization',
                'function': 'optimizeSSD',
                'category': 'system',
                'module_id': 'sys:optimize_ssd'
            },
            18: {
                'name': 'System Health Check',
                'module': 'scripts.health.system_health',
                'function': 'checkSystemHealth',
                'category': 'health',
                'module_id': 'health:services'
            },
            19: {
                'name': 'Graphics Card Check',
                'module': 'scripts.health.gpu_check',
                'function': 'checkGraphicsCard',
                'category': 'health',
                'module_id': 'health:gpu'
            },
            20: {
                'name': 'Automatic Updates Check',
                'module': 'scripts.system.auto_updates',
                'function': 'checkAutoUpdates',
                'category': 'system',
                'module_id': 'health:auto_updates'
            }
        }
        return chapters
    
    def createModuleIdMap(self) -> Dict[str, int]:
        """Create mapping from module IDs to chapter numbers."""
        module_map = {}
        for chapter_num, chapter_info in self.chapters.items():
            if chapter_info.get('module_id'):
                module_map[chapter_info['module_id']] = chapter_num
        return module_map
    
    def runChapter(self, chapter_num: int, chapter_info: Dict) -> bool:
        """Run a single chapter."""
        module_id = chapter_info.get('module_id', 'unknown')
        success = False
        
        # Emit begin marker
        print("::BEGIN module=" + module_id + " ts=" + 
              subprocess.check_output(['date', '-Iseconds']).decode().strip())
        sys.stdout.flush()
        
        # If running with logging, also set up module-specific log
        log_dir = os.environ.get('MINTY_LOG_DIR', '')
        module_log_path = ""
        if log_dir and os.path.exists(log_dir + "/modules"):
            # Sanitize module ID for filename
            safe_module_id = module_id.replace(':', '-')
            module_log_path = log_dir + "/modules/" + safe_module_id + ".log"
        
        try:
            # Check if module file exists
            module_path = chapter_info['module'].replace('.', '/') + '.py'
            if not os.path.exists(module_path):
                self.reporter.say("Chapter " + str(chapter_num) + " (" + 
                                chapter_info['name'] + ") not yet implemented")
                self.reporter.setChapterStatus(chapter_num, True, "Not implemented")
                success = True
            else:
                # Import module dynamically
                module = importlib.import_module(chapter_info['module'])
                function = getattr(module, chapter_info['function'])
                
                # If we have a module log path, create a subprocess to tee output
                if module_log_path and os.environ.get('MINTY_TEE'):
                    # Save current stdout/stderr
                    old_stdout = sys.stdout
                    old_stderr = sys.stderr
                    
                    # Create tee process for module logging
                    tee_proc = subprocess.Popen(
                        ['tee', '-a', module_log_path],
                        stdin=subprocess.PIPE,
                        stdout=old_stdout,
                        stderr=old_stderr,
                        text=True
                    )
                    
                    # Redirect stdout/stderr to tee
                    sys.stdout = tee_proc.stdin
                    sys.stderr = tee_proc.stdin
                    
                    try:
                        # Run the chapter function
                        success = function(self.reporter, self.runner)
                    finally:
                        # Restore stdout/stderr
                        sys.stdout = old_stdout
                        sys.stderr = old_stderr
                        tee_proc.stdin.close()
                        tee_proc.wait()
                else:
                    # Run normally without module logging
                    success = function(self.reporter, self.runner)
                    
        except Exception as e:
            self.reporter.say("Error running chapter " + str(chapter_num) + 
                            ": " + str(e), is_error=True)
            self.reporter.setChapterStatus(chapter_num, False, "Error: " + str(e)[:30])
            success = False
        
        # Emit end marker
        exit_code = 0 if success else 1
        print("::END module=" + module_id + " ts=" + 
              subprocess.check_output(['date', '-Iseconds']).decode().strip() + 
              " rc=" + str(exit_code))
        sys.stdout.flush()
        
        # Write audit log entry if enabled
        audit_log = os.environ.get('MINTY_LOG_DIR', '') + "/audit.jsonl"
        if os.path.exists(os.path.dirname(audit_log)):
            with open(audit_log, 'a') as f:
                timestamp = subprocess.check_output(['date', '-Iseconds']).decode().strip()
                audit_entry = {
                    "type": "module",
                    "id": module_id,
                    "rc": exit_code,
                    "ts": timestamp
                }
                f.write(json.dumps(audit_entry) + "\n")
        
        return success
    
    def run(self) -> None:
        """Run all maintenance tasks."""
        # Write report header
        self.reporter.writeHeader()
        
        # Determine which chapters to run
        if self.manifest:
            # Run only selected chapters from manifest
            chapters_to_run = []
            
            # Handle Timeshift specially if requested
            if self.manifest.get('create_timeshift', False):
                if 'sys:timeshift' in self.module_id_map:
                    chapters_to_run.append(self.module_id_map['sys:timeshift'])
            
            # Add selected modules
            for module_id in self.selected_modules:
                if module_id in self.module_id_map:
                    chapters_to_run.append(self.module_id_map[module_id])
            
            # Sort to maintain order
            chapters_to_run.sort()
            
            # Run selected chapters
            for chapter_num in chapters_to_run:
                chapter_info = self.chapters[chapter_num]
                self.runChapter(chapter_num, chapter_info)
        else:
            # Run all chapters (classic mode)
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
    parser = argparse.ArgumentParser(description='Linux Mint System Maintenance')
    parser.add_argument('--manifest', type=str, help='Path to manifest JSON file')
    parser.add_argument('mode', nargs='?', choices=['dry-run'], help='Run mode')
    
    args = parser.parse_args()
    
    # Handle dry-run from command line
    if args.mode == 'dry-run' and not args.manifest:
        # Classic dry-run mode - pass arguments through normally
        orchestrator = MaintenanceOrchestrator()
    else:
        # Either manifest mode or normal mode
        orchestrator = MaintenanceOrchestrator(manifest_path=args.manifest)
    
    orchestrator.run()


if __name__ == "__main__":
    main()

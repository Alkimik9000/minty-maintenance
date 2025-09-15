#!/usr/bin/env python3
"""
Chapter 8: Standalone Applications Check
Check for AppImages and applications in /opt that need manual updates.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner, getRealUserHome
from typing import List, Tuple
import glob


def checkStandaloneApps(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Check for standalone applications that need manual updates."""
    reporter.writeChapterHeader(8, "Checking Standalone Applications")
    
    reporter.say("\n🎯 Let me check for applications that need manual updates...")
    reporter.say("This includes AppImages and applications installed in /opt.")
    
    # Get real user home
    real_home = getRealUserHome()
    
    # Check for AppImages
    reporter.say("\n📦 Checking for AppImage applications...")
    appimages = findAppImages(real_home)
    
    if appimages:
        reporter.say("\n📋 Found " + str(len(appimages)) + " AppImage applications:")
        # Show up to 10 AppImages
        for i, app in enumerate(appimages[:10]):
            app_name = os.path.basename(app).replace('.AppImage', '')
            reporter.say("   • " + app_name)
        
        if len(appimages) > 10:
            reporter.say("   ... and " + str(len(appimages) - 10) + " more")
        
        reporter.say("\n💡 These apps need to be updated manually by downloading" +
                    " new versions from their websites. Consider switching to" +
                    " Flatpak versions if available for automatic updates.")
        
        appimage_note = "Found " + str(len(appimages)) + " AppImages"
    else:
        reporter.say("✅ No AppImage applications found. That's good -" +
                    " they're harder to keep updated!")
        appimage_note = "None found"
    
    # Check applications in /opt
    reporter.say("\n📁 Checking applications in /opt directory...")
    opt_apps, update_instructions = checkOptApplications()
    
    if opt_apps:
        reporter.say("\n📋 Found " + str(len(opt_apps)) + " applications in /opt:")
        for app in opt_apps:
            reporter.say("   • " + app)
        
        reporter.say("\n💡 Update instructions for these applications:")
        reporter.say(update_instructions)
        
        reporter.say("\n⚠️  These applications typically update through their" +
                    " own built-in updaters or need manual downloads.")
        
        notes = appimage_note + ", " + str(len(opt_apps)) + " /opt apps"
    else:
        notes = appimage_note
    
    reporter.setChapterStatus(8, True, notes)
    return True


def findAppImages(home_dir: str) -> List[str]:
    """Find all AppImage files in common locations."""
    search_paths = [
        os.path.join(home_dir, "Downloads"),
        os.path.join(home_dir, ".local", "bin"),
        os.path.join(home_dir, "Applications"),
        "/opt"
    ]
    
    appimages = []
    for path in search_paths:
        if os.path.exists(path):
            # Search for .AppImage files
            pattern = os.path.join(path, "**", "*.AppImage")
            found = glob.glob(pattern, recursive=True)
            appimages.extend(found)
    
    return list(set(appimages))  # Remove duplicates


def checkOptApplications() -> Tuple[List[str], str]:
    """Check for known applications in /opt directory."""
    opt_apps = []
    instructions = []
    
    # Define known applications and their update instructions
    known_apps = {
        "balena-etcher": ("Balena Etcher", "https://etcher.balena.io/"),
        "JDownloader": ("JDownloader", "Check built-in updater or https://jdownloader.org/"),
        "MediaElch": ("MediaElch", "https://www.kvibes.de/mediaelch/download/"),
        "Obsidian": ("Obsidian", "Check in-app updates or https://obsidian.md/"),
        "smartgit": ("SmartGit", "Check Help → Check for Updates"),
        "pdfstudio": ("PDF Studio", "Check Help menu for updates"),
        "WonderPen": ("WonderPen", "Check in-app updates"),
        "gitkraken": ("GitKraken", "Updates automatically or check Help menu"),
        "docker-desktop": ("Docker Desktop", "Check system tray icon for updates")
    }
    
    for dir_name, (app_name, update_info) in known_apps.items():
        # Check if directory exists (handle wildcards for pdfstudio*)
        if dir_name == "pdfstudio":
            if any(os.path.exists(os.path.join("/opt", d)) 
                   for d in os.listdir("/opt") if d.startswith("pdfstudio")):
                opt_apps.append(app_name)
                instructions.append("   • " + app_name + ": " + update_info)
        else:
            if os.path.exists(os.path.join("/opt", dir_name)):
                opt_apps.append(app_name)
                instructions.append("   • " + app_name + ": " + update_info)
    
    return opt_apps, "\n".join(instructions)


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = checkStandaloneApps(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

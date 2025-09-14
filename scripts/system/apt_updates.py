#!/usr/bin/env python3
"""
Chapter 3: APT System Updates
Updates core system software including security fixes and bug repairs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner
import subprocess


def aptExists() -> bool:
    """Return True if 'apt' exists on PATH."""
    path_env: str = os.environ.get("PATH", "")
    paths: list[str] = path_env.split(":") if path_env else []
    for p in paths:
        candidate: str = os.path.join(p, "apt")
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return True
    return False


def simulateDistUpgrade() -> tuple[int, list[str]]:
    """Simulate a dist-upgrade and return (count, first_five_highlights)."""
    env_copy: dict[str, str] = dict(os.environ)
    env_copy["LC_ALL"] = "C"
    env_copy["LANG"] = "C"
    proc = subprocess.run(
        [
            "apt-get",
            "-s",
            "-o",
            "APT::Get::Always-Include-Phased-Updates=true",
            "dist-upgrade",
        ],
        capture_output=True,
        text=True,
        check=False,
        env=env_copy,
    )
    stdout_text: str = proc.stdout or ""
    lines: list[str] = stdout_text.splitlines()
    inst_lines: list[str] = [ln for ln in lines if ln.startswith("Inst ")]
    highlights: list[str] = inst_lines[:5]
    return (len(inst_lines), highlights)


def simulateFixNeeded() -> bool:
    """Return True if a simulated '-f install' suggests changes are needed."""
    sim_fix = subprocess.run(
        ["apt-get", "-s", "-f", "install"],
        capture_output=True,
        text=True,
        check=False,
    )
    out_text: str = sim_fix.stdout or ""
    if "The following packages will be REMOVED" in out_text:
        return True
    if "The following additional packages will be installed" in out_text:
        return True
    if "The following packages will be upgraded" in out_text:
        return True
    return False


def performAptUpdates(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Perform APT system updates and cleanup."""
    reporter.writeChapterHeader(3, "Updating Your Core System Software")
    
    reporter.say("\n📦 Now for the important part - updating your system's" +
                " core software. This includes security fixes and bug repairs.")
    reporter.say("\nThis is like getting oil changes for your car - it keeps" +
                " everything running smoothly and safely.")
    
    if not aptExists():
        reporter.say("This system does not have APT. Skipping Chapter 3.", is_error=True)
        reporter.setChapterStatus(3, False, "Skipped: non-APT system")
        return False

    chapter_success: bool = True
    
    # Pre-update space check
    space_before_apt: int = reporter.getDiskSpace()
    
    # Refresh package list
    success, _ = runner.run(
        "refresh the list of available updates",
        ["sudo", "apt-get", "update"]
    )
    if not success:
        chapter_success = False
    
    # Handle interrupted dpkg state then check for broken packages
    runner.run("configure pending packages (if any)", ["sudo", "dpkg", "--configure", "-a"], check=False)

    reporter.say("\n🔧 Let me make sure nothing is broken before we start...")
    needs_fix: bool = simulateFixNeeded()
    success, _output = runner.run(
        "check and fix broken packages",
        ["sudo", "apt-get", "-f", "install", "-y"],
        check=False
    )
    if needs_fix and success:
        reporter.say("I repaired some package issues successfully.")
    elif needs_fix and not success:
        reporter.say("I tried to repair package issues but some problems remain.", is_error=True)
        chapter_success = False
    
    # Check what needs updating
    reporter.say("\n📋 Checking what needs updating...")
    try:
        update_count, highlights = simulateDistUpgrade()
    except Exception:
        update_count, highlights = 0, []
    if update_count < 0:
        update_count = 0
    if highlights:
        reporter.say("Here are some highlights:")
        for line in highlights:
            reporter.say("   " + line)
    
    if update_count > 0:
        reporter.say("I found " + str(update_count) + " updates available.")
        
        if not reporter.isDryRun():
            # Run the upgrade
            cmd: list[str] = [
                "sudo", "env", "DEBIAN_FRONTEND=noninteractive",
                "apt-get",
                "-o", "APT::Get::Always-Include-Phased-Updates=true",
                "-o", "Dpkg::Options::=--force-confdef",
                "-o", "Dpkg::Options::=--force-confold",
                "-y", "dist-upgrade",
            ]
            success, output = runner.run(
                "install all system updates",
                cmd
            )
            if not success:
                reporter.say("Some packages couldn't be upgraded.", is_error=True)
                reporter.say("This is usually fine - they'll update later.")
                chapter_success = False
            else:
                reporter.say("✅ All updates installed successfully!")
        else:
            reporter.say("(Test mode: I would install these updates now with 'apt-get dist-upgrade')")
    else:
        reporter.say("Great news! Your system is already up to date.")
    
    # Cleanup
    reporter.say("\n🧹 Now let me clean up old stuff you don't need...")
    success, _ = runner.run(
        "remove packages that are no longer needed",
        ["sudo", "apt-get", "autoremove", "--purge", "-y"]
    )
    if not success:
        chapter_success = False
    
    success, _ = runner.run(
        "clean up the package download cache",
        ["sudo", "apt-get", "autoclean"]
    )
    if not success:
        chapter_success = False
    
    # Calculate space saved
    space_after_apt: int = reporter.getDiskSpace()
    space_saved: int = reporter.calculateSpaceDiff(space_before_apt, space_after_apt)
    
    if space_saved > 0:
        notes: str = "Updated & freed " + str(space_saved) + "MB"
        reporter.space_changes[3] = space_saved if space_saved > 0 else 0
    else:
        notes = "Updated successfully"
    
    reporter.setChapterStatus(3, chapter_success, notes)
    return chapter_success


def checkAvailableUpdates(reporter: MaintenanceReporter) -> int:
    """Check how many updates are available."""
    try:
        result = subprocess.run(
            ["apt", "list", "--upgradable"],
            capture_output=True,
            text=True,
            check=False
        )
        
        lines = result.stdout.strip().split('\n')
        # Filter out the "Listing..." line and count actual packages
        update_lines = [line for line in lines if line and "upgradable" in line]
        
        # Show first few updates
        if update_lines:
            reporter.say("Here are some highlights:")
            for line in update_lines[:5]:
                reporter.say("   " + line)
        
        return len(update_lines)
    except:
        return 0


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = performAptUpdates(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

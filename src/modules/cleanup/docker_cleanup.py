#!/usr/bin/env python3
"""
Chapter 14: Docker Cleanup
Clean up Docker containers, images, and build cache.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.utils.utils import MaintenanceReporter, CommandRunner, checkCommandExists
import subprocess
import time


def cleanupDocker(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Clean up Docker resources."""
    reporter.writeChapterHeader(14, "Cleaning Up Docker Containers")
    
    reporter.say("\n🐳 Docker is used for running containerized applications." +
                " Let me check if cleanup is needed...")
    
    chapter_success = True
    
    if not checkCommandExists("docker"):
        reporter.say("Docker is not installed. That's fine unless you're" +
                    " a developer using containers.")
        reporter.setChapterStatus(14, True, "Not installed")
        return True
    
    # Check if Docker daemon is running
    if not isDockerRunning():
        reporter.say("\nDocker is installed but not running. Let me start it...")
        if not reporter.isDryRun():
            success = startDocker(reporter, runner)
            if not success:
                reporter.setChapterStatus(14, False, "Docker not running")
                return False
        else:
            reporter.say("(Test mode: Would start Docker service)")
    
    # If Docker is running, proceed with cleanup
    if isDockerRunning() or reporter.isDryRun():
        # Show current usage
        reporter.say("\n📊 Current Docker disk usage:")
        showDockerUsage(reporter)
        
        # Explain what will be cleaned
        reporter.say("\n🔍 Checking what can be cleaned up...")
        reporter.say("This would remove:")
        reporter.say("   • All stopped containers")
        reporter.say("   • All networks not used by containers")
        reporter.say("   • All dangling images")
        reporter.say("   • All build cache")
        
        # Count what would be removed
        stopped_containers = countStoppedContainers()
        dangling_images = countDanglingImages()
        
        if stopped_containers > 0 or dangling_images > 0:
            reporter.say("\n⚠️  Found " + str(stopped_containers) + 
                        " stopped containers and " + str(dangling_images) + 
                        " unused images.")
            
            if not reporter.isDryRun():
                reporter.say("\nCleaning up safely...")
                
                # Remove old stopped containers
                success, _ = runner.run(
                    "remove old stopped containers",
                    ["docker", "container", "prune", "-f", "--filter", "until=24h"],
                    check=False
                )
                
                # Remove dangling images
                success, _ = runner.run(
                    "remove unused images",
                    ["docker", "image", "prune", "-f"],
                    check=False
                )
                
                # Clean old build cache
                success, _ = runner.run(
                    "clean old build cache",
                    ["docker", "builder", "prune", "-f", "--filter", "until=168h"],
                    check=False
                )
            else:
                reporter.say("(Test mode: Would clean Docker resources)")
        else:
            reporter.say("✅ Docker is already clean!")
        
        # Show new usage
        reporter.say("\n📊 Docker disk usage after cleanup:")
        showDockerUsage(reporter)
        
        reporter.setChapterStatus(14, chapter_success, "Docker cleaned safely")
    
    return chapter_success


def isDockerRunning() -> bool:
    """Check if Docker daemon is running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            check=False
        )
        return result.returncode == 0
    except:
        return False


def startDocker(reporter: MaintenanceReporter, runner: CommandRunner) -> bool:
    """Try to start Docker service."""
    success, _ = runner.run(
        "start Docker service",
        ["sudo", "systemctl", "start", "docker"],
        check=False
    )
    
    if success:
        reporter.say("✅ Docker started successfully!")
        time.sleep(2)  # Give it time to initialize
        return True
    else:
        reporter.say("Couldn't start Docker. You may need to check it manually.", 
                    is_error=True)
        return False


def showDockerUsage(reporter: MaintenanceReporter) -> None:
    """Show Docker disk usage."""
    try:
        result = subprocess.run(
            ["docker", "system", "df"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            reporter.say(result.stdout)
    except:
        pass


def countStoppedContainers() -> int:
    """Count stopped Docker containers."""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "-q", "-f", "status=exited"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            lines = [line for line in result.stdout.strip().split('\n') if line]
            return len(lines)
        return 0
    except:
        return 0


def countDanglingImages() -> int:
    """Count dangling Docker images."""
    try:
        result = subprocess.run(
            ["docker", "images", "-q", "-f", "dangling=true"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            lines = [line for line in result.stdout.strip().split('\n') if line]
            return len(lines)
        return 0
    except:
        return 0


def main() -> None:
    """Main entry point when run as standalone script."""
    reporter = MaintenanceReporter()
    runner = CommandRunner(reporter)
    
    success = cleanupDocker(reporter, runner)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

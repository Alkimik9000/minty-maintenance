#!/usr/bin/env bash
# System Maintenance Script for Linux Mint 22 (Ubuntu 24.04 base)
# Unified Update & Maintenance — User-Friendly Report Edition
# Desktop: GNOME 46 on Xorg • GPU: NVIDIA GTX 1080 (proprietary)
#
# Usage:
# bash update_all_improved.sh          # full run
# bash update_all_improved.sh dry-run  # simulate; no changes
#
# This version produces a user-friendly report that explains
# everything in simple terms for non-technical users.

set -Euo pipefail
shopt -s nullglob

# Ensure we always get to the summary
trap 'echo "Script encountered an error but continuing to summary..."' ERR

# ------------------------------------------------------------
# Config & paths
# ------------------------------------------------------------
DRY_RUN=${1:-}
if [[ "$DRY_RUN" == "dry-run" ]]; then
    DRY_RUN=true
else
    DRY_RUN=false
fi

# Save report in current directory
REPORT_DIR="$(pwd)"
mkdir -p "$REPORT_DIR"
TS=$(date +%Y%m%d-%H%M%S)
REPORT="$REPORT_DIR/system-maintenance-report-$TS.txt"

# Fixed-width chapter header lines (readable in terminal)
CH_WIDTH=72

# Track chapter statuses for summary table
declare -A chapter_status
declare -A chapter_notes
declare -A space_changes

# Store initial disk space
INITIAL_SPACE=$(df -h / | tail -1 | awk '{print $4}')

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
hr() {
    local char=${1:-"-"}
    printf "%-${CH_WIDTH}s\n" "" | tr " " "$char"
}

# Friendly narration for non-technical users
say() {
    echo -e "$@" | fold -s -w 72 | tee -a "$REPORT"
}

# Error-aware narration
error_say() {
    echo -e "⚠️  $@" | fold -s -w 72 | tee -a "$REPORT"
}

chapter() {
    local num="$1"; shift
    echo "" | tee -a "$REPORT"
    echo "# ------------------------------------------------------------" | tee -a "$REPORT"
    printf "# Chapter %s — %s\n" "$num" "$@" | tee -a "$REPORT"
    echo "# ------------------------------------------------------------" | tee -a "$REPORT"
    echo "" | tee -a "$REPORT"
}

# Calculate space difference
calc_space_diff() {
    local before="$1"
    local after="$2"
    # Convert human-readable to MB
    local before_mb=$(echo "$before" | \
        sed 's/G/*1024/; s/M//; s/K/\/1024/' | bc 2>/dev/null || echo 0)
    local after_mb=$(echo "$after" | \
        sed 's/G/*1024/; s/M//; s/K/\/1024/' | bc 2>/dev/null || echo 0)
    echo $((after_mb - before_mb))
}

# Run a command with friendly explanation
run() {
    local desc="$1"; shift
    say "\n🔧 Now I'm going to: $desc"
    
    if [[ $DRY_RUN == true ]]; then
        say "   (Test mode: Just checking what would happen)"
        say "   Command: $*"
        return 0
    fi
    
    # Capture space before operation
    local space_before=$(df -h / | tail -1 | awk '{print $4}')
    
    # Run command and capture output
    local output_file=$(mktemp)
    local error_file=$(mktemp)
    
    if "$@" >"$output_file" 2>"$error_file"; then
        local ec=$?
        # Show relevant output
        if [[ -s "$output_file" ]]; then
            # Filter and show only important lines
            grep -E "(upgraded|removed|freed|installed|cleaned)" \
                "$output_file" 2>/dev/null | head -5 | \
                sed 's/^/   /' | tee -a "$REPORT" || true
        fi
        
        # Calculate space change
        local space_after=$(df -h / | tail -1 | awk '{print $4}')
        local space_diff=$(calc_space_diff "$space_before" "$space_after")
        
        if [[ $space_diff -gt 0 ]]; then
            say "   ✅ Done! This freed up about ${space_diff}MB of space."
        elif [[ $space_diff -lt 0 ]]; then
            say "   ✅ Done! This used about ${space_diff#-}MB of space."
        else
            say "   ✅ Done! Everything completed successfully."
        fi
        
        rm -f "$output_file" "$error_file"
        return 0
    else
        local ec=$?
        error_say "Something didn't work as expected. Let me explain:"
        
        # Analyze and explain the error
        local error_content=$(cat "$error_file" 2>/dev/null || echo "")
        
        if [[ "$error_content" == *"permission denied"* ]]; then
            error_say "This needs administrator privileges. You might" \
                "need to enter your password."
        elif [[ "$error_content" == *"not found"* ]]; then
            error_say "The program I need isn't installed yet. This" \
                "is normal - I'll try to install it for you."
        elif [[ "$error_content" == *"Unable to lock"* ]]; then
            error_say "Another update program is running. Please close" \
                "Software Updater or Synaptic and try again."
        elif [[ "$error_content" == *"No space left"* ]]; then
            error_say "Your disk is full! We need to free up space" \
                "before continuing. Try emptying your trash."
        else
            error_say "Technical details: $error_content"
        fi
        
        # Show first few lines of error
        head -3 "$error_file" 2>/dev/null | sed 's/^/   /' | \
            tee -a "$REPORT" || true
        
        rm -f "$output_file" "$error_file"
        return $ec
    fi
}

# ------------------------------------------------------------
# Welcome & Introduction
# ------------------------------------------------------------
{
    echo "🖥️  SYSTEM MAINTENANCE REPORT"
    echo "============================"
    echo
    echo "Hello! I'm your computer maintenance assistant."
    echo "Today is $(date '+%A, %B %d, %Y at %I:%M %p')"
    echo
    echo "I'm going to help keep your computer running smoothly by:"
    echo "• Installing security updates"
    echo "• Cleaning up unnecessary files"
    echo "• Checking your system's health"
    echo "• Making sure everything is up-to-date"
    echo
    echo "Mode: $([[ $DRY_RUN == true ]] && \
        echo 'Test Run (no changes will be made)' || \
        echo 'Full Maintenance')"
    echo "Your system: Linux Mint 22 with GNOME desktop"
    echo "This report: $REPORT"
    echo
    echo "📑 What I'll Do Today:"
    echo "----------------------"
    echo "1. Create a Safety Checkpoint"
    echo "2. Update Command-Line Tools (Homebrew)"
    echo "3. Update System Software (APT)"
    echo "4. Check for Package Issues"
    echo "5. Update Desktop Applications (Flatpak)"
    echo "6. Update Snap Applications"
    echo "7. Update Python Tools"
    echo "8. Check Standalone Applications"
    echo "9. Update Device Firmware"
    echo "10. Clean Up Old Log Files"
    echo "11. Remove Old System Kernels"
    echo "12. Check Hard Drive Health"
    echo "13. Update Desktop Extensions"
    echo "14. Clean Up Docker Containers"
    echo "15. Refresh File Search Database"
    echo "16. Deep Clean Temporary Files"
    echo "17. Optimize SSD Performance"
    echo "18. Check System Health"
    echo "19. Check Graphics Card"
    echo "20. Verify Automatic Updates"
    echo "21. Final Summary"
    echo
    echo "Let's begin! This usually takes 10-30 minutes."
    echo
} > "$REPORT"

# ------------------------------------------------------------
# Chapter 1 — Timeshift Safety Checkpoint
# ------------------------------------------------------------
chapter 1 "Creating a Safety Checkpoint"
chapter_success=true

say "\n📸 First, let me mark your current system state as a" \
    "safe point to return to if needed."
say "\nThink of this like saving your game before a boss fight -" \
    "if anything goes wrong, we can restore everything back to" \
    "exactly how it is right now."

if command -v timeshift >/dev/null 2>&1; then
    say "\n🔍 Checking your backup system..."
    
    # Get Timeshift info with better debugging
    say "Getting Timeshift configuration..."
    ts_list_output=$(sudo timeshift --list 2>&1 || true)
    
    # Show relevant parts for debugging
    if [[ $DRY_RUN == true ]]; then
        echo "$ts_list_output" | grep -E "(Backend|Device|Location)" | \
            sed 's/^/   DEBUG: /' | tee -a "$REPORT" || true
    fi
    
    backend=$(echo "$ts_list_output" | grep -oP 'Backend.*:\s*\K\S+' || \
        echo "RSYNC")
    
    say "Detected backend: $backend"
    
    if [[ "$backend" == "BTRFS" ]]; then
        error_say "You're using BTRFS backups. I can see your" \
            "backups but can't add notes to them automatically." \
            "You can add notes manually in the Timeshift program."
        chapter_notes[1]="BTRFS mode - manual notes only"
        chapter_success=false
    else
        # Try multiple methods to find snapshot location
        snapshot_root=""
        
        # Method 1: Parse from timeshift --list
        snapshot_root=$(echo "$ts_list_output" | \
            grep -oP 'Snapshot [Ll]ocation.*:\s*\K.*' | \
            sed 's/[[:space:]]*$//' || true)
        
        # Method 2: Check common external drive locations
        if [[ -z "$snapshot_root" ]] || [[ ! -d "$snapshot_root/snapshots" ]]; then
            say "Searching for Timeshift snapshots on external drives..."
            # Use SUDO_USER if running with sudo
            REAL_USER=${SUDO_USER:-$USER}
            for mount in /media/$REAL_USER/* /mnt/*; do
                if [[ -d "$mount/timeshift/snapshots" ]]; then
                    snapshot_root="$mount/timeshift"
                    say "Found snapshots at: $snapshot_root"
                    break
                fi
            done
        fi
        
        # Method 3: Check default location
        if [[ -z "$snapshot_root" ]] || [[ ! -d "$snapshot_root/snapshots" ]]; then
            if [[ -d "/timeshift/snapshots" ]]; then
                snapshot_root="/timeshift"
            fi
        fi
        
        if [[ -n "$snapshot_root" ]] && [[ -d "$snapshot_root/snapshots" ]]; then
            snapshots_dir="$snapshot_root/snapshots"
            say "Looking for snapshots in: $snapshots_dir"
            
            # Find latest snapshot WITH info.json file
            latest_dir=""
            say "Finding latest snapshot with configuration file..."
            
            # Sort snapshots by date and check each for info.json
            while IFS= read -r snapshot_dir; do
                if [[ -f "$snapshot_dir/info.json" ]]; then
                    latest_dir="$snapshot_dir"
                    break
                fi
            done < <(sudo ls -1dt "$snapshots_dir"/* 2>/dev/null || true)
            
            if [[ -n "$latest_dir" && -d "$latest_dir" ]]; then
                snapshot_name=$(basename "$latest_dir")
                say "\n✅ Found your latest complete backup: $snapshot_name"
                
                # Create human-readable timestamp
                PRETTY_DATE=$(date '+%A, %B %d, %Y')
                PRETTY_TIME=$(date '+%I:%M %p')
                PRETTY_DATETIME=$(date '+%B %d, %Y at %I:%M %p')
                
                # Add maintenance note
                info_json="$latest_dir/info.json"
                if [[ -f "$info_json" ]]; then
                    # Install jq if needed
                    if ! command -v jq >/dev/null 2>&1; then
                        run "install the JSON tool I need (jq)" \
                            sudo apt install -y jq || true
                    fi
                    
                    if command -v jq >/dev/null 2>&1; then
                        # Create detailed maintenance note
                        MAINT_NOTE="🔧 SYSTEM MAINTENANCE CHECKPOINT"
                        MAINT_NOTE+="\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                        MAINT_NOTE+="\n📅 Date: $PRETTY_DATE"
                        MAINT_NOTE+="\n🕐 Time: $PRETTY_TIME"
                        MAINT_NOTE+="\n"
                        MAINT_NOTE+="\n✅ This snapshot was marked before running:"
                        MAINT_NOTE+="\n   • System updates (APT, Flatpak, Snap)"
                        MAINT_NOTE+="\n   • Security patches"
                        MAINT_NOTE+="\n   • Cleanup operations"
                        MAINT_NOTE+="\n   • Firmware updates"
                        MAINT_NOTE+="\n"
                        MAINT_NOTE+="\n💡 Safe to restore if any issues occur after maintenance."
                        MAINT_NOTE+="\n"
                        MAINT_NOTE+="\nCreated by: System Maintenance Script"
                        MAINT_NOTE+="\nTimestamp: $(date '+%Y-%m-%d %H:%M:%S')"
                        
                        if [[ $DRY_RUN == false ]]; then
                            # Show what we're about to do
                            say "Adding maintenance note to snapshot..."
                            
                            # Backup original
                            if cp -a "$info_json" "$info_json.bak.$TS"; then
                                say "   ✓ Backed up original info.json"
                            fi
                            
                            # Update with proper ownership preservation
                            if jq --arg note "$MAINT_NOTE" \
                                '.comments = (if .comments then ($note + "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + .comments) else $note end)' \
                                "$info_json" > "$info_json.tmp"; then
                                
                                # Preserve ownership and permissions
                                chown --reference="$info_json" "$info_json.tmp"
                                chmod --reference="$info_json" "$info_json.tmp"
                                
                                if mv "$info_json.tmp" "$info_json"; then
                                    say "✅ Successfully added maintenance checkpoint!"
                                    say "   The snapshot now shows:"
                                    say "   • When: $PRETTY_DATETIME"
                                    say "   • Why: Pre-maintenance safety checkpoint"
                                    chapter_notes[1]="Checkpoint marked at $PRETTY_TIME"
                                    
                                    # Show preview of the comment
                                    say "\nPreview of snapshot comment:"
                                    jq -r '.comments' "$info_json" 2>/dev/null | \
                                        head -5 | sed 's/^/   /' | tee -a "$REPORT" || true
                                else
                                    error_say "Failed to update info.json"
                                    chapter_success=false
                                fi
                            else
                                error_say "Failed to process JSON"
                                chapter_success=false
                            fi
                        else
                            say "(Test mode: Would add this note to snapshot)"
                            echo -e "$MAINT_NOTE" | head -10 | \
                                sed 's/^/   /' | tee -a "$REPORT"
                        fi
                    else
                        error_say "jq is required to add comments. Please install it."
                        chapter_notes[1]="Missing jq tool"
                        chapter_success=false
                    fi
                else
                    error_say "No info.json found in snapshot directory!"
                    say "Contents of $latest_dir:"
                    ls -la "$latest_dir" | head -5 | sed 's/^/   /' | \
                        tee -a "$REPORT" || true
                    chapter_notes[1]="Missing info.json"
                    chapter_success=false
                fi
            else
                error_say "No snapshots found! Please create one first."
                say "You can create a snapshot using the Timeshift GUI."
                chapter_notes[1]="No snapshots exist"
                chapter_success=false
            fi
        else
            error_say "Could not find Timeshift snapshot location!"
            say "Please ensure:"
            say "   • Timeshift is configured"
            say "   • Your backup drive is mounted"
            say "   • Snapshots exist"
            
            # Show what we tried
            say "\nSearched in:"
            say "   • Parsed location: ${snapshot_root:-none}"
            say "   • External drives: /media/$USER/*"
            say "   • Default: /timeshift"
            
            chapter_notes[1]="Cannot find snapshots"
            chapter_success=false
        fi
    fi
else
    error_say "Timeshift isn't installed. This is your backup" \
        "system - I highly recommend installing it!"
    say "To install: sudo apt install timeshift"
    chapter_notes[1]="Timeshift not installed"
    chapter_success=false
fi

chapter_status[1]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 2 — Homebrew Updates
# ------------------------------------------------------------
chapter 2 "Updating Command-Line Tools (Homebrew)"
chapter_success=true

say "\n🍺 Homebrew manages special command-line tools that" \
    "aren't in the regular software store."

if command -v brew >/dev/null 2>&1; then
    say "\nLet me check for updates to your command-line tools..."
    
    run "check for new versions" brew update || \
        { chapter_success=false; }
    run "install the updates" brew upgrade || \
        { chapter_success=false; }
    
    chapter_notes[2]="Tools updated"
else
    say "You don't have Homebrew installed. That's fine -" \
        "you probably don't need it unless you're a developer."
    chapter_notes[2]="Not installed (optional)"
fi

chapter_status[2]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 3 — APT System Updates
# ------------------------------------------------------------
chapter 3 "Updating Your Core System Software"
chapter_success=true

say "\n📦 Now for the important part - updating your system's" \
    "core software. This includes security fixes and bug repairs."

say "\nThis is like getting oil changes for your car - it keeps" \
    "everything running smoothly and safely."

# Pre-update space check
space_before_apt=$(df -h / | tail -1 | awk '{print $4}')

run "refresh the list of available updates" \
    sudo apt update || { chapter_success=false; }

# Check for broken packages first
say "\n🔧 Let me make sure nothing is broken before we start..."
if ! sudo apt -f install -y 2>&1 | grep -q "0 upgraded"; then
    say "I fixed some package issues for you!"
fi

# Show what will be updated
say "\n📋 Checking what needs updating..."
update_list=$(apt list --upgradable 2>/dev/null | grep -v "Listing" || true)
update_count=$(echo "$update_list" | grep -c "upgradable" 2>/dev/null || true)
update_count=${update_count:-0}

if [[ $update_count -gt 0 ]]; then
    say "I found $update_count updates available. Here are some highlights:"
    echo "$update_list" | head -5 | sed 's/^/   /' | tee -a "$REPORT"
    
    if [[ $DRY_RUN == false ]]; then
        # Run the upgrade and capture any errors
        if ! sudo apt -o APT::Get::Always-Include-Phased-Updates=true \
            --allow-downgrades full-upgrade -y 2>&1 | tee -a "$REPORT"; then
            error_say "Some packages couldn't be upgraded."
            say "This is usually fine - they'll update later."
            chapter_success=false
        else
            say "✅ All updates installed successfully!"
        fi
    else
        say "(Test mode: I would install these updates now)"
    fi
else
    say "Great news! Your system is already up to date."
fi

# Cleanup
say "\n🧹 Now let me clean up old stuff you don't need..."
run "remove packages that are no longer needed" \
    sudo apt autoremove --purge -y || { chapter_success=false; }
run "clean up the package download cache" \
    sudo apt clean || { chapter_success=false; }

# Calculate space saved
space_after_apt=$(df -h / | tail -1 | awk '{print $4}')
space_saved=$(calc_space_diff "$space_before_apt" "$space_after_apt")

if [[ $space_saved -gt 0 ]]; then
    chapter_notes[3]="Updated & freed ${space_saved}MB"
    space_changes[3]=$space_saved
else
    chapter_notes[3]="Updated successfully"
fi

chapter_status[3]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 4 — Package Sanity Checks
# ------------------------------------------------------------
chapter 4 "Checking for Package Issues"
chapter_success=true

say "\n🔍 Let me check if any software is being held back or" \
    "if there are any orphaned packages taking up space..."

# Check for held packages
held_packages=$(apt-mark showhold 2>/dev/null || true)
if [[ -n "$held_packages" ]]; then
    error_say "These packages are being held back from updates:"
    echo "$held_packages" | sed 's/^/   /' | tee -a "$REPORT"
    say "This might be intentional, but if you don't know why" \
        "they're held, you might want to investigate."
    chapter_notes[4]="Found held packages"
else
    say "✅ No packages are being held back. Good!"
fi

# Check for orphaned packages
if ! command -v deborphan >/dev/null 2>&1; then
    run "install tool to find orphaned packages" \
        sudo apt install -y deborphan || true
fi

if command -v deborphan >/dev/null 2>&1; then
    orphans=$(deborphan 2>/dev/null || true)
    if [[ -n "$orphans" ]]; then
        orphan_count=$(echo "$orphans" | wc -l)
        say "\n🧹 Found $orphan_count orphaned packages that" \
            "aren't needed anymore:"
        echo "$orphans" | head -5 | sed 's/^/   /' | tee -a "$REPORT"
        
        if [[ $DRY_RUN == false ]]; then
            # Remove orphans one by one to avoid xargs issues
            say "\nRemoving orphaned packages..."
            while IFS= read -r pkg; do
                if [[ -n "$pkg" ]]; then
                    run "remove orphaned package: $pkg" \
                        sudo apt remove -y "$pkg" || \
                        { chapter_success=false; }
                fi
            done <<< "$orphans"
        fi
        chapter_notes[4]="Cleaned $orphan_count orphans"
    else
        say "✅ No orphaned packages found. Your system is tidy!"
        chapter_notes[4]="No issues found"
    fi
fi

chapter_status[4]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 5 — Flatpak Applications
# ------------------------------------------------------------
chapter 5 "Updating Desktop Applications (Flatpak)"
chapter_success=true

say "\n📱 Flatpak apps are like phone apps - they run in their" \
    "own secure space and update independently."

if command -v flatpak >/dev/null 2>&1; then
    # Check if any remotes are configured
    remote_count=$(flatpak remote-list 2>/dev/null | wc -l || echo "0")
    
    if [[ $remote_count -eq 0 ]]; then
        error_say "Flatpak is installed but not set up yet."
        say "You can add the Flathub store with:"
        say "flatpak remote-add --if-not-exists flathub" \
            "https://flathub.org/repo/flathub.flatpakrepo"
        chapter_notes[5]="Not configured"
        chapter_success=false
    else
        say "\n🔄 Updating your Flatpak applications..."
        
        # Show what's installed
        app_count=$(flatpak list --app 2>/dev/null | wc -l || echo "0")
        say "You have $app_count Flatpak apps installed."
        
        run "update all Flatpak apps" flatpak update -y || \
            { chapter_success=false; }
        run "remove unused Flatpak data" \
            flatpak uninstall --unused -y || \
            { chapter_success=false; }
        
        chapter_notes[5]="$app_count apps updated"
    fi
else
    say "Flatpak isn't installed. It's a great way to get the" \
        "latest versions of apps like Spotify, Discord, etc."
    chapter_notes[5]="Not installed (optional)"
fi

chapter_status[5]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 6 — Snap Applications
# ------------------------------------------------------------
chapter 6 "Updating Snap Applications"
chapter_success=true

say "\n📦 Snap is another app system, similar to Flatpak." \
    "Let me check for updates and clean up old versions..."

if command -v snap >/dev/null 2>&1; then
    # Check current settings
    current_retain=$(snap get system refresh.retain 2>/dev/null || \
        echo "default")
    
    say "Snap keeps old versions of apps as backups. I'll limit" \
        "this to save space."
    
    if [[ "$current_retain" != "2" ]]; then
        run "set Snap to keep only 2 old versions" \
            sudo snap set system refresh.retain=2 || \
            { chapter_success=false; }
    fi
    
    # Update snaps
    run "update all Snap applications" sudo snap refresh || \
        { chapter_success=false; }
    
    # Clean up old revisions
    say "\n🧹 Removing old app versions to free up space..."
    old_snaps=$(snap list --all | awk '/disabled/{print $1, $3}')
    
    if [[ -n "$old_snaps" ]]; then
        while read -r name rev; do
            if [[ -n "$name" && -n "$rev" ]]; then
                if [[ $DRY_RUN == true ]]; then
                    say "Would remove old version: $name (revision $rev)"
                else
                    sudo snap remove "$name" --revision="$rev" 2>&1 | \
                        grep -E "(removed|freeing)" | tee -a "$REPORT" || true
                fi
            fi
        done <<< "$old_snaps"
        chapter_notes[6]="Updated & cleaned old versions"
    else
        say "✅ No old versions to clean up."
        chapter_notes[6]="Updated, already clean"
    fi
else
    say "Snap isn't installed. That's fine - Flatpak is usually" \
        "preferred anyway."
    chapter_notes[6]="Not installed (optional)"
fi

chapter_status[6]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 7 — Python Package Updates
# ------------------------------------------------------------
chapter 7 "Updating Python Tools"
chapter_success=true

say "\n🐍 If you have any Python tools installed, let me" \
    "update them for you..."

if command -v pip >/dev/null 2>&1; then
    say "\nPython tools are programming utilities. Even if you're" \
        "not a programmer, some apps might have installed these."
    
    # Check for pipx instead (recommended for Ubuntu 24.04)
    if ! command -v pipx >/dev/null 2>&1; then
        say "\nUbuntu 24.04 recommends using pipx for Python tools."
        run "install pipx for safe Python package management" \
            sudo apt install -y pipx || { chapter_success=false; }
    fi
    
    say "\n💡 Note: Ubuntu 24.04 protects system Python. Use pipx" \
        "for installing Python applications safely."
    
    # For user Python packages, check if they use pipx
    if command -v pipx >/dev/null 2>&1; then
        say "\nChecking pipx-managed Python applications..."
        pipx_list=$(pipx list 2>/dev/null || true)
        if [[ -n "$pipx_list" ]]; then
            run "upgrade all pipx-managed applications" \
                pipx upgrade-all || { chapter_success=false; }
        else
            say "No pipx applications installed."
        fi
        chapter_notes[7]="Pipx apps checked"
    else
        chapter_notes[7]="System Python protected"
    fi
else
    say "No Python package manager found. That's normal if" \
        "you're not doing any programming."
    chapter_notes[7]="Not needed"
fi

chapter_status[7]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 8 — Standalone Applications Check
# ------------------------------------------------------------
chapter 8 "Checking Standalone Applications"
chapter_success=true

say "\n🎯 Let me check for applications that need manual updates..."
say "This includes AppImages and applications installed in /opt."

# Get real user home (not root when using sudo)
REAL_HOME=$(getent passwd ${SUDO_USER:-$USER} | cut -d: -f6)

# First check for AppImages
say "\n📦 Checking for AppImage applications..."
search_paths=("$REAL_HOME/Downloads" "$REAL_HOME/.local/bin" \
    "$REAL_HOME/Applications" "/opt")

# Use null delimiter to handle spaces in filenames
# Wrap in error handling to ensure script continues
if mapfile -d '' -t appimages < <(find "${search_paths[@]}" \
    -maxdepth 3 -type f -name "*.AppImage" -print0 2>/dev/null); then
    : # Success
else
    appimages=() # Empty array on error
fi

if ((${#appimages[@]} > 0)); then
    say "\n📋 Found ${#appimages[@]} AppImage applications:"
    # Show up to 10 AppImages
    count=0
    for app in "${appimages[@]}"; do
        if [[ $count -ge 10 ]]; then
            say "   ... and $((${#appimages[@]} - 10)) more"
            break
        fi
        # Handle empty entries
        if [[ -z "$app" ]]; then
            continue
        fi
        app_name=$(basename "$app" .AppImage)
        say "   • $app_name"
        ((count++)) || true
    done
    
    say "\n💡 These apps need to be updated manually by downloading" \
        "new versions from their websites. Consider switching to" \
        "Flatpak versions if available for automatic updates."
    
    chapter_notes[8]="Found ${#appimages[@]} AppImages"
else
    say "✅ No AppImage applications found. That's good -" \
        "they're harder to keep updated!"
    chapter_notes[8]="None found"
fi

# Now check for other applications in /opt
say "\n📁 Checking applications in /opt directory..."

# List of known applications that might need updates
opt_apps=()
update_instructions=""

# Check each application
if [[ -d "/opt/balena-etcher" ]]; then
    opt_apps+=("Balena Etcher")
    update_instructions+="\n   • Balena Etcher: https://etcher.balena.io/"
fi

if [[ -d "/opt/JDownloader" ]]; then
    opt_apps+=("JDownloader")
    update_instructions+="\n   • JDownloader: Check built-in updater or https://jdownloader.org/"
fi

if [[ -d "/opt/MediaElch" ]]; then
    opt_apps+=("MediaElch")
    update_instructions+="\n   • MediaElch: https://www.kvibes.de/mediaelch/download/"
fi

if [[ -d "/opt/Obsidian" ]]; then
    opt_apps+=("Obsidian")
    update_instructions+="\n   • Obsidian: Check in-app updates or https://obsidian.md/"
fi

if [[ -d "/opt/smartgit" ]]; then
    opt_apps+=("SmartGit")
    update_instructions+="\n   • SmartGit: Check Help → Check for Updates"
fi

if [[ -d "/opt/pdfstudio"* ]]; then
    opt_apps+=("PDF Studio")
    update_instructions+="\n   • PDF Studio: Check Help menu for updates"
fi

if [[ -d "/opt/WonderPen" ]]; then
    opt_apps+=("WonderPen")
    update_instructions+="\n   • WonderPen: Check in-app updates"
fi

if [[ -d "/opt/gitkraken" ]]; then
    opt_apps+=("GitKraken")
    update_instructions+="\n   • GitKraken: Updates automatically or check Help menu"
fi

if [[ -d "/opt/docker-desktop" ]]; then
    opt_apps+=("Docker Desktop")
    update_instructions+="\n   • Docker Desktop: Check system tray icon for updates"
fi

# Report findings
if [[ ${#opt_apps[@]} -gt 0 ]]; then
    say "\n📋 Found ${#opt_apps[@]} applications in /opt:"
    for app in "${opt_apps[@]}"; do
        say "   • $app"
    done
    
    say "\n💡 Update instructions for these applications:"
    echo -e "$update_instructions" | tee -a "$REPORT"
    
    say "\n⚠️  These applications typically update through their" \
        "own built-in updaters or need manual downloads."
    
    chapter_notes[8]="Found ${#appimages[@]} AppImages, ${#opt_apps[@]} /opt apps"
else
    chapter_notes[8]="Found ${#appimages[@]} AppImages"
fi

chapter_status[8]="✅ Success"

# ------------------------------------------------------------
# Chapter 9 — Firmware Updates
# ------------------------------------------------------------
chapter 9 "Checking Device Firmware Updates"
chapter_success=true

say "\n🔧 Firmware is the low-level software that runs your" \
    "hardware devices. Let me check if any updates are available..."

if command -v fwupdmgr >/dev/null 2>&1; then
    say "\nThis might find updates for:"
    say "   • Your computer's BIOS/UEFI"
    say "   • SSD/hard drive firmware"
    say "   • Thunderbolt controllers"
    say "   • Other hardware components"
    
    run "refresh firmware update list" fwupdmgr refresh || \
        { chapter_success=false; }
    
    # Check for updates
    say "\n🔍 Checking what firmware updates are available..."
    if fwupdmgr get-updates 2>&1 | tee -a "$REPORT" | \
        grep -q "No updates available"; then
        say "✅ All firmware is up to date!"
        chapter_notes[9]="All up to date"
    else
        if [[ $DRY_RUN == false ]]; then
            say "\n⚠️ Firmware updates found! These are important" \
                "for stability and security."
            run "install firmware updates" fwupdmgr update || \
                { chapter_success=false; }
            
            say "\n⚠️ IMPORTANT: You may need to restart your" \
                "computer for firmware updates to complete!"
            chapter_notes[9]="Updates installed - restart needed"
        else
            say "(Test mode: Would check for firmware updates)"
            chapter_notes[9]="No updates needed"
        fi
    fi
else
    error_say "Firmware updater not installed. Install it with:"
    say "sudo apt install fwupd"
    chapter_notes[9]="fwupd not installed"
    chapter_success=false
fi

chapter_status[9]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 10 — Journal Cleanup
# ------------------------------------------------------------
chapter 10 "Cleaning Up System Log Files"
chapter_success=true

say "\n📚 Your system keeps detailed logs of everything it does." \
    "Over time, these can take up quite a bit of space."

say "\nLet me clean up logs older than 2 weeks..."

# Check current journal size
journal_size=$(journalctl --disk-usage 2>&1 | \
    grep -oP '\d+\.?\d*[MG]' || echo "unknown")
say "Current log storage: $journal_size"

run "clean up old system logs (keep 2 weeks)" \
    sudo journalctl --vacuum-time=2weeks --vacuum-size=500M || \
    { chapter_success=false; }

# Check new size
new_journal_size=$(journalctl --disk-usage 2>&1 | \
    grep -oP '\d+\.?\d*[MG]' || echo "unknown")
say "Log storage after cleanup: $new_journal_size"

chapter_notes[10]="Cleaned to $new_journal_size"
chapter_status[10]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 11 — Old Kernel Cleanup
# ------------------------------------------------------------
chapter 11 "Removing Old System Kernels"
chapter_success=true

say "\n🖥️ The kernel is the core of your operating system." \
    "When it updates, old versions are kept as backups."

say "\nLet me clean up old kernels, keeping the newest 2..."

# Install tool if needed
if ! command -v purge-old-kernels >/dev/null 2>&1; then
    run "install kernel cleanup tool" \
        sudo apt install -y byobu || { chapter_success=false; }
fi

# Check current kernels
kernel_count=$(dpkg -l | grep -c "^ii.*linux-image-[0-9]" || echo "0")
say "You currently have $kernel_count kernels installed."

if [[ $kernel_count -gt 2 ]]; then
    # Check for held kernels
    held_kernels=$(apt-mark showhold | grep linux-image || true)
    if [[ -n "$held_kernels" ]]; then
        error_say "These kernels are being held:"
        echo "$held_kernels" | sed 's/^/   /' | tee -a "$REPORT"
    fi
    
    # The correct syntax without --keep for this version
    run "remove old kernels (keeping newest 2)" \
        sudo purge-old-kernels -y 2 || \
        { chapter_success=false; }
    
    chapter_notes[11]="Cleaned old kernels"
else
    say "✅ You only have $kernel_count kernels. No cleanup needed!"
    chapter_notes[11]="Already clean"
fi

chapter_status[11]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 12 — Disk Health Check
# ------------------------------------------------------------
chapter 12 "Checking Hard Drive Health"
chapter_success=true

say "\n💾 Let me check if your storage drives are healthy..."

# Install SMART tools if needed
if ! command -v smartctl >/dev/null 2>&1; then
    run "install disk health monitoring tools" \
        sudo apt install -y smartmontools || { chapter_success=false; }
fi

if command -v smartctl >/dev/null 2>&1; then
    # Find all disk devices
    mapfile -t disks < <(lsblk -ndo TYPE,NAME | \
        awk '$1=="disk"{print $2}')
    
    if ((${#disks[@]} > 0)); then
        say "\nChecking ${#disks[@]} storage device(s)..."
        
        all_healthy=true
        for disk in "${disks[@]}"; do
            # Skip zram devices (compressed RAM, not physical disks)
            if [[ "$disk" == zram* ]]; then
                continue
            fi
            
            say "\n📊 Checking /dev/$disk..."
            
            if sudo smartctl -H "/dev/$disk" 2>&1 | \
                grep -q "PASSED"; then
                say "   ✅ Healthy!"
            else
                error_say "   ⚠️ This drive may have issues!" \
                    "Consider backing up important data."
                all_healthy=false
                chapter_success=false
            fi
        done
        
        if [[ $all_healthy == true ]]; then
            chapter_notes[12]="All drives healthy"
        else
            chapter_notes[12]="Drive issues detected!"
        fi
        
        say "\n💡 Tip: For a thorough test, run:" \
            "sudo smartctl -t long /dev/sdX"
        say "   (Replace sdX with your drive name)"
    fi
else
    error_say "Could not check disk health."
    chapter_notes[12]="Tools not available"
fi

chapter_status[12]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 13 — GNOME Extensions
# ------------------------------------------------------------
chapter 13 "Updating Desktop Extensions"
chapter_success=true

say "\n🧩 GNOME extensions customize your desktop experience." \
    "Let me check for updates..."

if command -v gnome-extensions >/dev/null 2>&1; then
    # List enabled extensions
    # Count enabled extensions (trim whitespace)
    enabled_ext=$(gnome-extensions list --enabled 2>/dev/null | \
        wc -l | tr -d ' ' || echo "0")
    
    if [[ $enabled_ext -gt 0 ]]; then
        say "You have $enabled_ext extensions enabled."
        
        run "update GNOME extensions" \
            gnome-extensions update || { chapter_success=false; }
        
        say "\n💡 For more control, use the Extension Manager app" \
            "from Software Center."
        chapter_notes[13]="$enabled_ext extensions updated"
    else
        say "No extensions are currently enabled."
        chapter_notes[13]="No extensions enabled"
    fi
else
    say "GNOME extensions system not found. You can install" \
        "Extension Manager from Software Center for easy management."
    chapter_notes[13]="Not available"
fi

chapter_status[13]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 14 — Docker Cleanup
# ------------------------------------------------------------
chapter 14 "Cleaning Up Docker Containers"
chapter_success=true

say "\n🐳 Docker is used for running containerized applications." \
    "Let me check if cleanup is needed..."

if command -v docker >/dev/null 2>&1; then
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        # Try to start Docker if not running
        say "\nDocker is installed but not running. Let me start it..."
        if [[ $DRY_RUN == false ]]; then
            if sudo systemctl start docker 2>/dev/null; then
                say "✅ Docker started successfully!"
                sleep 2 # Give it time to initialize
            else
                error_say "Couldn't start Docker. You may need to check it manually."
                chapter_notes[14]="Docker not running"
                chapter_success=false
            fi
        else
            say "(Test mode: Would start Docker service)"
        fi
    fi
    
    # If Docker is running (or we just started it)
    if docker info >/dev/null 2>&1; then
        # Show current usage
        say "\n📊 Current Docker disk usage:"
        docker system df 2>/dev/null | tee -a "$REPORT" || true
        
        # Check what would be removed
        say "\n🔍 Checking what can be cleaned up..."
        say "This would remove:"
        say "   • All stopped containers"
        say "   • All networks not used by containers"
        say "   • All dangling images"
        say "   • All build cache"
        
        # Count what would be removed
        stopped_containers=$(docker ps -a -q -f status=exited | wc -l || echo "0")
        dangling_images=$(docker images -q -f dangling=true | wc -l || echo "0")
        
        if [[ $stopped_containers -gt 0 ]] || [[ $dangling_images -gt 0 ]]; then
            say "\n⚠️  Found $stopped_containers stopped containers and" \
                "$dangling_images unused images."
            
            if [[ $DRY_RUN == false ]]; then
                # Safer cleanup - only remove truly unused items
                say "\nCleaning up safely..."
                
                # Remove only stopped containers older than 24h
                run "remove old stopped containers" \
                    docker container prune -f --filter "until=24h" || true
                
                # Remove only dangling images
                run "remove unused images" \
                    docker image prune -f || true
                
                # Clean build cache older than 7 days
                run "clean old build cache" \
                    docker builder prune -f --filter "until=168h" || true
            else
                say "(Test mode: Would clean Docker resources)"
            fi
        else
            say "✅ Docker is already clean!"
        fi
        
        # Show new usage
        say "\n📊 Docker disk usage after cleanup:"
        docker system df 2>/dev/null | tee -a "$REPORT" || true
        
        chapter_notes[14]="Docker cleaned safely"
    fi
else
    say "Docker is not installed. That's fine unless you're" \
        "a developer using containers."
    chapter_notes[14]="Not installed"
fi

chapter_status[14]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 15 — Update File Search Database
# ------------------------------------------------------------
chapter 15 "Refreshing File Search Database"
chapter_success=true

say "\n🔍 Your system maintains a database of all files for" \
    "quick searching. Let me update it..."

say "\nThis helps the 'locate' command find files instantly."

# Check if database is recent
db_file="/var/lib/mlocate/mlocate.db"
if [[ -f "$db_file" ]]; then
    db_age_hours=$(( ($(date +%s) - $(stat -c %Y "$db_file")) / 3600 ))
    
    if [[ $db_age_hours -lt 24 ]]; then
        say "✅ Database was updated $db_age_hours hours ago." \
            "Still fresh!"
        chapter_notes[15]="Already up to date"
    else
        say "Database is $db_age_hours hours old. Updating..."
        
        if command -v updatedb >/dev/null 2>&1; then
            run "scan all files and update search database" \
                sudo updatedb || { chapter_success=false; }
            chapter_notes[15]="Database refreshed"
        else
            run "install file search tools" \
                sudo apt install -y mlocate || { chapter_success=false; }
            run "build initial database" \
                sudo updatedb || { chapter_success=false; }
            chapter_notes[15]="Installed and initialized"
        fi
        
        say "\n⏱️ Note: This can take a while on large drives" \
            "with many files (like cloud storage folders)."
    fi
else
    say "No file database found. Installing search tools..."
    run "install file search tools" \
        sudo apt install -y mlocate || { chapter_success=false; }
    run "build initial database" \
        sudo updatedb || { chapter_success=false; }
    chapter_notes[15]="Installed and initialized"
fi

chapter_status[15]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 16 — BleachBit Deep Clean
# ------------------------------------------------------------
chapter 16 "Deep Cleaning Temporary Files"
chapter_success=true

say "\n🧹 BleachBit is like CCleaner for Linux - it removes" \
    "temporary files, caches, and other junk."

if command -v bleachbit >/dev/null 2>&1; then
    say "\nThis will clean things like:"
    say "   • Web browser caches"
    say "   • Temporary files"
    say "   • Old logs"
    say "   • Thumbnail caches"
    
    # Get list of cleaners
    say "\n📋 Available cleaning options:"
    bleachbit --list-cleaners 2>/dev/null | head -10 | \
        sed 's/^/   /' | tee -a "$REPORT" || true
    
    # Clean common safe items
    run "perform deep clean (browser cache, temp files, logs)" \
        bleachbit --clean system.cache system.tmp || \
        { chapter_success=false; }
    
    say "\n💡 Run BleachBit (GUI) to customize what gets cleaned."
    chapter_notes[16]="Deep cleaned"
else
    say "BleachBit is not installed. It's a great tool for" \
        "freeing up disk space!"
    say "Install it from Software Center or with:" \
        "sudo apt install bleachbit"
    chapter_notes[16]="Not installed (optional)"
fi

chapter_status[16]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 17 — SSD Optimization
# ------------------------------------------------------------
chapter 17 "Optimizing SSD Performance"
chapter_success=true

say "\n⚡ If you have an SSD (solid-state drive), it needs" \
    "periodic optimization to maintain performance."

say "\nThis process is called 'trimming' and helps the drive" \
    "manage deleted data efficiently."

run "optimize all SSD drives" sudo fstrim -av || \
    { chapter_success=false; }

say "\n📝 Note: You'll see errors for non-SSD drives or" \
    "filesystems that don't support trimming. This is normal!"

say "\n💡 Your system should do this automatically weekly," \
    "but running it manually ensures it's done."

chapter_notes[17]="SSDs optimized"
chapter_status[17]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 18 — System Health Check
# ------------------------------------------------------------
chapter 18 "Checking Overall System Health"
chapter_success=true

say "\n🏥 Let me run a quick health check on your system..."

# Check for failed services
say "\n🔴 Checking for failed services..."
failed_services=$(systemctl --failed --no-pager --no-legend 2>/dev/null || true)

if [[ -z "$failed_services" ]]; then
    say "✅ All system services are running properly!"
    chapter_notes[18]="All services healthy"
else
    error_say "Found some services with issues:"
    echo "$failed_services" | sed 's/^/   /' | tee -a "$REPORT"
    say "\nThese might need attention, but many are not critical."
    chapter_notes[18]="Some service issues"
    chapter_success=false
fi

# Check for critical errors in logs
say "\n📊 Checking system logs for critical issues..."
critical_errors=$(journalctl -p 3 -xb --no-pager 2>/dev/null | \
    tail -5 | grep -v "^--" || true)

if [[ -n "$critical_errors" ]]; then
    say "Found some system warnings (most are usually harmless):"
    echo "$critical_errors" | sed 's/^/   /' | tee -a "$REPORT"
else
    say "✅ No critical errors in recent logs!"
fi

chapter_status[18]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 19 — NVIDIA Graphics Check
# ------------------------------------------------------------
chapter 19 "Checking Graphics Card Status"
chapter_success=true

say "\n🎮 You have an NVIDIA GTX 1080 graphics card." \
    "Let me check its status..."

if command -v nvidia-smi >/dev/null 2>&1; then
    # Get GPU info
    gpu_info=$(nvidia-smi \
        --query-gpu=driver_version,name,memory.total,temperature.gpu \
        --format=csv,noheader 2>/dev/null || true)
    
    if [[ -n "$gpu_info" ]]; then
        IFS=',' read -r driver gpu mem temp <<< "$gpu_info"
        
        say "\n✅ Graphics card detected!"
        say "   • Card: $gpu"
        say "   • Driver: $driver"
        say "   • Memory: $mem"
        say "   • Temperature: ${temp}°C"
        
        if [[ ${temp%.*} -gt 80 ]]; then
            error_say "⚠️ Your GPU is running hot! Check for dust" \
                "in the fans or improve case ventilation."
        fi
        
        chapter_notes[19]="GPU healthy, driver $driver"
    else
        error_say "Could not read GPU information."
        chapter_notes[19]="GPU detection issue"
        chapter_success=false
    fi
else
    error_say "NVIDIA drivers don't seem to be properly installed."
    say "Your graphics might be using basic drivers."
    chapter_notes[19]="NVIDIA tools not found"
    chapter_success=false
fi

chapter_status[19]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 20 — Automatic Updates Check
# ------------------------------------------------------------
chapter 20 "Verifying Automatic Security Updates"
chapter_success=true

say "\n🔒 Ubuntu can install security updates automatically" \
    "in the background. Let me check if this is enabled..."

if dpkg -l unattended-upgrades 2>/dev/null | grep -q "^ii"; then
    # Check if it's enabled
    auto_enabled=$(apt-config dump 2>/dev/null | \
        grep -i "APT::Periodic::Unattended-Upgrade" | \
        grep -oP '"\K[^"]+' || echo "0")
    
    if [[ "$auto_enabled" == "1" ]]; then
        say "✅ Automatic security updates are ENABLED!"
        say "Your system installs critical security fixes" \
            "automatically, keeping you safe."
        chapter_notes[20]="Auto-updates enabled"
    else
        error_say "⚠️ Automatic updates are DISABLED!"
        say "I recommend enabling this for better security."
        say "To enable: sudo dpkg-reconfigure unattended-upgrades"
        chapter_notes[20]="Auto-updates disabled"
        chapter_success=false
    fi
    
    # Show last run time
    last_run="/var/log/unattended-upgrades/unattended-upgrades.log"
    if [[ -f "$last_run" ]]; then
        last_date=$(tail -n 50 "$last_run" 2>/dev/null | \
            grep -oP '\d{4}-\d{2}-\d{2}' | tail -1 || echo "unknown")
        say "Last automatic update check: $last_date"
    fi
else
    error_say "Automatic updates are not installed!"
    say "I strongly recommend installing this for security:"
    say "sudo apt install unattended-upgrades"
    say "Then enable with: sudo dpkg-reconfigure unattended-upgrades"
    chapter_notes[20]="Not installed"
    chapter_success=false
fi

chapter_status[20]=$([[ $chapter_success == true ]] && \
    echo "✅ Success" || echo "⚠️ Needs Attention")

# ------------------------------------------------------------
# Chapter 21 — Final Summary
# ------------------------------------------------------------
chapter 21 "Maintenance Complete!"

# Calculate total space change
final_space=$(df -h / | tail -1 | awk '{print $4}')
total_space_change=$(calc_space_diff "$INITIAL_SPACE" "$final_space")

say "\n🎉 All done! Here's what happened today:"
say

# Summary table
{
    printf "\n%-30s | %-20s | %-30s\n" \
        "Task" "Status" "Notes"
    printf "%-30s | %-20s | %-30s\n" \
        "------------------------------" \
        "--------------------" \
        "------------------------------"
    
    for i in {1..20}; do
        # Get chapter name
        case $i in
            1) task="Safety Checkpoint" ;;
            2) task="Homebrew Tools" ;;
            3) task="System Updates" ;;
            4) task="Package Cleanup" ;;
            5) task="Flatpak Apps" ;;
            6) task="Snap Apps" ;;
            7) task="Python Tools" ;;
            8) task="AppImage Check" ;;
            9) task="Firmware Updates" ;;
            10) task="Log Cleanup" ;;
            11) task="Kernel Cleanup" ;;
            12) task="Disk Health" ;;
            13) task="GNOME Extensions" ;;
            14) task="Docker Cleanup" ;;
            15) task="Search Database" ;;
            16) task="Deep Clean" ;;
            17) task="SSD Optimization" ;;
            18) task="System Health" ;;
            19) task="Graphics Card" ;;
            20) task="Auto Updates" ;;
        esac
        
        status="${chapter_status[$i]:-Unknown}"
        notes="${chapter_notes[$i]:-No data}"
        
        printf "%-30s | %-20s | %-30s\n" \
            "$task" "$status" "$notes"
    done
} | tee -a "$REPORT"

say "\n📊 Space Summary:"
if [[ $total_space_change -gt 0 ]]; then
    say "   🎉 Freed up approximately ${total_space_change}MB!"
elif [[ $total_space_change -lt -100 ]]; then
    say "   📈 Used ${total_space_change#-}MB (updates need space)"
else
    say "   ↔️ Disk space remained about the same"
fi
say "   Available space: $final_space"

# Count issues
issues=0
for status in "${chapter_status[@]}"; do
    [[ "$status" == *"Attention"* ]] && ((issues++))
done

say "\n📋 Overall Assessment:"
if [[ $issues -eq 0 ]]; then
    say "   🌟 Your system is in excellent shape!"
    say "   All maintenance tasks completed successfully."
elif [[ $issues -le 3 ]]; then
    say "   👍 Your system is in good shape overall."
    say "   A few minor items need attention when convenient."
else
    say "   ⚠️ Several items need your attention."
    say "   Review the orange items above for details."
fi

# Check for reboot
if [[ -f /var/run/reboot-required ]]; then
    say "\n🔄 IMPORTANT: A restart is required!"
    say "   Some updates (like kernel or firmware) need a"
    say "   restart to take effect. Please restart soon."
fi

say "\n💾 This report has been saved to:"
say "   $REPORT"

say "\n🗓️ When to run maintenance again:"
say "   • Weekly: For best performance and security"
say "   • Monthly: Minimum recommended frequency"
say "   • After major system changes or if issues arise"

say "\n👋 Thank you for maintaining your system!"
say "   Your computer appreciates the care!"

# Desktop notification
if [[ $DRY_RUN == false ]] && command -v notify-send >/dev/null 2>&1; then
    if [[ $issues -eq 0 ]]; then
        notify-send "✅ Maintenance Complete!" \
            "All tasks successful. Report saved."
    else
        notify-send "⚠️ Maintenance Complete" \
            "$issues items need attention. Check report."
    fi
fi

chapter_status[21]="✅ Complete"

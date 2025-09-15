#!/usr/bin/env python3
"""
🍃 minty-maintenance Interactive TUI
Mouse-friendly, colorful maintenance module selector with tri-state checkboxes
"""

import json
import re
import subprocess
import tempfile
import asyncio
import datetime
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from textual import on, work
from textual.events import Click
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer, VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Checkbox, Header, Label, Static, ProgressBar, RichLog, Footer
from textual.message import Message
from textual.screen import Screen
from textual.timer import Timer


# Sanitization for Textual widget IDs (which cannot contain colons)
_ID_SAFE = re.compile(r"[^A-Za-z0-9_-]")

def makeWidgetId(module_id: str) -> str:
    """Convert module ID to valid Textual widget ID"""
    # Replace any disallowed chars (like ':') with '-'
    safe: str = _ID_SAFE.sub("-", module_id)
    # Ensure it doesn't begin with a digit
    if safe and safe[0].isdigit():
        safe = "_" + safe
    return "cb-" + safe

# Global map: widget id -> original module id (with colon)
WIDGET_ID_TO_MODULE_ID: Dict[str, str] = {}

def _getModuleIdFromWidgetId(widget_id: str) -> str:
    """Get original module ID from sanitized widget ID"""
    return WIDGET_ID_TO_MODULE_ID.get(widget_id, "")


@dataclass
class ModuleItem:
    """Represents a maintenance module"""
    id: str
    label: str
    description: str
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    checked: bool = False
    partial: bool = False  # For parent items with mixed children states
    expanded: bool = True
    enabled: bool = True


def buildCheckbox(label: str, *, value: bool, enabled: bool, widget_id: str, classes: str = "module-checkbox") -> Checkbox:
    """Build a properly styled checkbox widget"""
    cb = Checkbox(label=label, value=value, id=widget_id, classes=classes)
    cb.disabled = not enabled
    # Don't let it expand to full height/width
    cb.styles.height = "auto"
    cb.styles.width = "1fr"
    cb.styles.margin = (0, 0)
    cb.styles.padding = (0, 1)
    cb.styles.content_align = ("left", "middle")
    return cb


class ModuleTree(Widget):
    """Tree widget for module selection with collapsible groups"""
    
    def __init__(self, modules: Dict[str, ModuleItem], **kwargs) -> None:
        super().__init__(**kwargs)
        self.modules = modules
        self.checkboxes: Dict[str, Checkbox] = {}
        self.selected_module: Optional[str] = None
    
    def compose(self) -> ComposeResult:
        """Build the module tree"""
        with ScrollableContainer(id="module-container"):
            # Group modules by category
            groups = {
                "sys": ("🔧 System Maintenance", [
                    ("sys:timeshift", "Create safety checkpoint (Timeshift)"),
                    ("sys:update_apt", "Update APT core packages"),
                    ("sys:manage_kernels", "Manage old kernels"),
                    ("sys:update_firmware", "Update device firmware"),
                    ("sys:optimize_ssd", "Optimize SSD"),
                ]),
                "apps": ("📱 Application Management", [
                    ("apps:update_flatpak", "Update Flatpak apps"),
                    ("apps:update_snap", "Update Snap packages"),
                    ("apps:check_brew", "Check Homebrew tools"),
                    ("apps:update_python", "Update Python packages"),
                    ("apps:scan_standalone", "Detect standalone app updates"),
                ]),
                "clean": ("🧹 Cleanup Operations", [
                    ("clean:orphans", "Remove orphaned packages"),
                    ("clean:logs", "Clean system logs"),
                    ("clean:docker", "Clean Docker containers/images"),
                    ("clean:bleachbit", "Deep clean (BleachBit)"),
                    ("clean:updatedb", "Update file search database"),
                ]),
                "health": ("🏥 Health Checks", [
                    ("health:disk", "Disk health"),
                    ("health:services", "System services"),
                    ("health:gpu", "GPU status"),
                    ("health:auto_updates", "Automatic updates enabled"),
                ]),
            }
            
            for group_id, (group_label, items) in groups.items():
                # Group title as a static label
                group_title = Label(group_label, id="hdr-" + group_id, classes="group-title")
                yield group_title
                
                # Immediately render the item checkboxes for the group (always visible)
                for item_id, item_label in items:
                    module = self.modules.get(item_id, ModuleItem(item_id, item_label, ""))
                    safe_id = makeWidgetId(item_id)
                    WIDGET_ID_TO_MODULE_ID[safe_id] = item_id
                    
                    # Handle partial state in label for parent items
                    label_to_show = item_label
                    if module.children and module.partial:
                        label_to_show = "[-] " + item_label
                    
                    cb = Checkbox(label=label_to_show, value=module.checked, id=safe_id, classes="module-checkbox")
                    cb.disabled = not module.enabled
                    cb.styles.height = "auto"
                    cb.styles.min_height = 1
                    cb.styles.margin = 0
                    cb.styles.padding = (0, 1, 0, 3)  # Extra left padding for indentation
                    cb.styles.content_align = ("left", "middle")
                    
                    self.checkboxes[item_id] = cb
                    yield cb
    
    def updateTriState(self, module_id: str) -> None:
        """Update tri-state logic for parent/child relationships"""
        # Update parent state based on children
        for group_id in ["sys", "apps", "clean", "health"]:
            children_ids = [mid for mid in self.modules if mid.startswith(group_id + ":")]
            if children_ids:
                checked_count = sum(1 for cid in children_ids if self.modules[cid].checked)
                
                # Update visual state for group header
                if checked_count == 0:
                    # All unchecked
                    pass
                elif checked_count == len(children_ids):
                    # All checked
                    pass
                else:
                    # Partial state
                    pass
    
    @on(Checkbox.Changed)
    def onCheckboxChanged(self, event: Checkbox.Changed) -> None:
        """Handle checkbox state changes"""
        # Be tolerant of Textual versions: sender/control/checkbox
        cb = getattr(event, "checkbox", None) or getattr(event, "control", None) or getattr(event, "sender", None)
        if cb is None:
            return
        widget_id: str = getattr(cb, "id", "") or ""
        module_id: str = _getModuleIdFromWidgetId(widget_id)
        if not module_id:
            return  # unknown; safety guard
            
        new_value: bool = bool(getattr(event, "value", getattr(cb, "value", False)))
        
        # Update model for that module_id
        self.setModuleChecked(module_id, new_value)
        
        # If it's a parent, cascade to children
        if self.isParent(module_id):
            self.setChildrenChecked(module_id, new_value)
        
        # Bubble up tri-state to ancestors (recompute parent partial/checked)
        self.recomputeTriStateUp(module_id)
        
        # Refresh visible labels for parents (add/remove "[-] " prefix)
        self.refreshParentLabels()
        
        self.post_message(ModuleTree.ModuleChanged(module_id, new_value))
    
    class ModuleChanged(Message):
        """Message sent when a module selection changes"""
        def __init__(self, module_id: str, checked: Optional[bool]) -> None:
            self.module_id = module_id
            self.checked = checked
            super().__init__()
    
    
    def setModuleChecked(self, module_id: str, checked: bool) -> None:
        """Set the checked state of a module"""
        if module_id in self.modules:
            self.modules[module_id].checked = checked
            self.modules[module_id].partial = False
    
    def isParent(self, module_id: str) -> bool:
        """Check if a module is a parent (has children)"""
        return bool(self.modules.get(module_id, ModuleItem("", "", "")).children)
    
    def setChildrenChecked(self, parent_id: str, checked: bool) -> None:
        """Set all children of a parent to the same checked state"""
        parent = self.modules.get(parent_id)
        if parent and parent.children:
            for child_id in parent.children:
                if child_id in self.modules:
                    self.modules[child_id].checked = checked
                    self.modules[child_id].partial = False
                    # Update checkbox widget if exists
                    if child_id in self.checkboxes:
                        self.checkboxes[child_id].value = checked
    
    def recomputeTriStateUp(self, from_id: str) -> None:
        """Recompute tri-state for parent groups based on children"""
        # For now, handle group-level tri-state
        # Find which group this module belongs to
        group_id = from_id.split(":")[0] if ":" in from_id else None
        if not group_id:
            return
            
        # Get all children in this group
        children_ids = [mid for mid in self.modules if mid.startswith(group_id + ":")]
        if not children_ids:
            return
            
        checked_count = sum(1 for cid in children_ids if self.modules[cid].checked)
        
        # Update parent group state (if we track group modules)
        if group_id in self.modules:
            if checked_count == 0:
                self.modules[group_id].checked = False
                self.modules[group_id].partial = False
            elif checked_count == len(children_ids):
                self.modules[group_id].checked = True
                self.modules[group_id].partial = False
            else:
                self.modules[group_id].checked = False
                self.modules[group_id].partial = True
    
    def refreshParentLabels(self) -> None:
        """Refresh checkbox labels to show partial state"""
        for module_id, module in self.modules.items():
            if module_id in self.checkboxes:
                checkbox = self.checkboxes[module_id]
                base_label = module.label
                
                # Add partial indicator if needed
                if module.children and module.partial:
                    checkbox.label = "[-] " + base_label
                else:
                    # Remove partial indicator if present
                    if str(checkbox.label).startswith("[-] "):
                        checkbox.label = base_label


class RunView(Screen):
    """Screen for showing live maintenance run progress"""
    
    def __init__(self, manifest_path: str, dry_run: bool, selected_count: int) -> None:
        super().__init__()
        self.manifest_path = manifest_path
        self.dry_run = dry_run
        self.selected_count = selected_count
        self.current_module = ""
        self.completed_modules = 0
        self.failed_modules = 0
        self.process: Optional[asyncio.subprocess.Process] = None
        self.log_dir = ""
        self.run_id = ""
        self.start_time = datetime.datetime.now()
        self.elapsed_timer: Optional[Timer] = None
        
    def compose(self) -> ComposeResult:
        """Build the run view UI"""
        yield Header(show_clock=True)
        
        # Progress section
        with Container(id="progress-container"):
            yield Label("Minty Maintenance — Running...", id="run-title")
            yield Label("Initializing...", id="current-module")
            yield ProgressBar(total=self.selected_count, id="progress-bar")
            yield Label("Elapsed: 00:00", id="elapsed-time")
        
        # Log viewer
        yield RichLog(highlight=True, markup=True, wrap=True, id="log-viewer")
        
        # Footer with controls
        with Container(id="footer-controls"):
            yield Button("Stop", id="btn-stop", variant="error")
            yield Button("View Logs", id="btn-view-logs", disabled=True)
            yield Button("Back to Menu", id="btn-back", disabled=True)
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Start the maintenance run when mounted"""
        self.elapsed_timer = self.set_interval(1.0, self.updateElapsedTime)
        self.runMaintenance()
    
    def updateElapsedTime(self) -> None:
        """Update the elapsed time display"""
        elapsed = datetime.datetime.now() - self.start_time
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)
        elapsed_label = self.query_one("#elapsed-time", Label)
        elapsed_label.update("Elapsed: " + str(minutes).zfill(2) + ":" + str(seconds).zfill(2))
    
    @work(thread=False)
    async def runMaintenance(self) -> None:
        """Run the maintenance script asynchronously"""
        log_viewer = self.query_one("#log-viewer", RichLog)
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        
        # Get script path
        script_path = Path(__file__).parent.parent.parent / "tools" / "mint-maintainer-runner.sh"
        if not script_path.exists():
            log_viewer.write("[red]Error: mint-maintainer-runner.sh not found[/red]")
            self.onComplete(success=False)
            return
        
        # Prepare environment
        env = os.environ.copy()
        env["MINTY_TEE"] = "1"
        
        # Generate run ID (will be overridden by the script, but good to have)
        self.run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        
        try:
            # Start the process
            self.process = await asyncio.create_subprocess_exec(
                "bash", str(script_path), "--manifest", self.manifest_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=env
            )
            
            # Stream output line by line
            while True:
                if not self.process.stdout:
                    break
                    
                line_bytes = await self.process.stdout.readline()
                if not line_bytes:
                    break
                
                line = line_bytes.decode('utf-8', errors='replace').rstrip()
                
                # Parse structured markers
                if line.startswith("::BEGIN module="):
                    # Extract module ID
                    parts = line.split()
                    for part in parts:
                        if part.startswith("module="):
                            module_id = part.split("=", 1)[1]
                            self.current_module = module_id
                            module_label = self.query_one("#current-module", Label)
                            module_label.update("Module " + str(self.completed_modules + 1) + "/" + 
                                              str(self.selected_count) + ": " + module_id)
                            log_viewer.write("[dim]" + line + "[/dim]")
                            break
                elif line.startswith("::END module="):
                    # Extract module ID and return code
                    parts = line.split()
                    rc = 0
                    for part in parts:
                        if part.startswith("rc="):
                            rc = int(part.split("=", 1)[1])
                            break
                    
                    self.completed_modules += 1
                    if rc != 0:
                        self.failed_modules += 1
                        log_viewer.write("[red]" + line + "[/red]")
                    else:
                        log_viewer.write("[green]" + line + "[/green]")
                    
                    progress_bar.update(progress=self.completed_modules)
                elif line.startswith("Log directory: "):
                    # Extract log directory
                    self.log_dir = line.split(": ", 1)[1].strip()
                    log_viewer.write("[blue]" + line + "[/blue]")
                else:
                    # Regular output
                    log_viewer.write(line)
            
            # Wait for process to complete
            await self.process.wait()
            
            # Handle completion
            success = self.process.returncode == 0
            self.onComplete(success=success)
            
        except Exception as e:
            log_viewer.write("[red]Error: " + str(e) + "[/red]")
            self.onComplete(success=False)
    
    def onComplete(self, success: bool) -> None:
        """Handle completion of the run"""
        if self.elapsed_timer:
            self.elapsed_timer.stop()
        
        # Update UI
        title_label = self.query_one("#run-title", Label)
        title_label.update("Minty Maintenance — Complete" if success else "Minty Maintenance — Failed")
        
        current_label = self.query_one("#current-module", Label)
        current_label.update("Completed: " + str(self.completed_modules) + " modules, " + 
                           str(self.failed_modules) + " failed")
        
        # Enable buttons
        self.query_one("#btn-stop", Button).disabled = True
        self.query_one("#btn-view-logs", Button).disabled = False
        self.query_one("#btn-back", Button).disabled = False
        
        log_viewer = self.query_one("#log-viewer", RichLog)
        log_viewer.write("")
        log_viewer.write("=" * 60)
        log_viewer.write("[bold]Run Summary:[/bold]")
        log_viewer.write("- Total modules: " + str(self.selected_count))
        log_viewer.write("- Completed: " + str(self.completed_modules))
        log_viewer.write("- Failed: " + str(self.failed_modules))
        if self.log_dir:
            log_viewer.write("- Logs saved to: " + self.log_dir)
    
    @on(Button.Pressed, "#btn-stop")
    async def onStop(self, event: Button.Pressed) -> None:
        """Handle stop button"""
        if self.process and self.process.returncode is None:
            self.process.terminate()
            await asyncio.sleep(0.5)
            if self.process.returncode is None:
                self.process.kill()
            
            log_viewer = self.query_one("#log-viewer", RichLog)
            log_viewer.write("[yellow]Run cancelled by user[/yellow]")
    
    @on(Button.Pressed, "#btn-view-logs")
    def onViewLogs(self, event: Button.Pressed) -> None:
        """Handle view logs button"""
        if self.log_dir:
            log_viewer = self.query_one("#log-viewer", RichLog)
            log_viewer.write("")
            log_viewer.write("[bold]Log Files:[/bold]")
            log_viewer.write("- Master log: " + self.log_dir + "/run.log")
            log_viewer.write("- Audit log: " + self.log_dir + "/audit.jsonl")
            log_viewer.write("- Module logs: " + self.log_dir + "/modules/")
            log_viewer.write("- Report: " + self.log_dir + "/report.txt")
            log_viewer.write("")
            log_viewer.write("[dim]Copy path to view in file manager[/dim]")
    
    @on(Button.Pressed, "#btn-back")
    def onBack(self, event: Button.Pressed) -> None:
        """Return to main menu"""
        self.app.pop_screen()


class MaintenanceTUI(App):
    """Main TUI application for minty-maintenance"""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    
    #settings-bar, #actions-bar {
        height: auto;
        padding: 0 1;
        content-align: left middle;
        border: none;
        background: $panel;
    }
    
    #settings-bar {
        border-bottom: solid $primary;
    }
    
    #actions-bar {
        border-top: solid $primary;
    }
    
    #module-scroll {
        height: 1fr;
        padding: 0 1;
    }
    
    .group-title {
        height: auto;
        padding: 0 1;
        text-style: bold;
        color: $accent;
        border: none;
        margin-top: 1;
    }
    
    .module-checkbox {
        height: auto;
        min-height: 1;
        padding: 0 1;
        margin: 0;
        border: none;
    }
    
    .module-checkbox:hover {
        background: $primary 10%;
    }
    
    .module-checkbox:disabled {
        opacity: 50%;
    }
    
    .bar Button {
        margin: 0 1;
    }
    
    .primary {
        text-style: bold;
    }
    
    #status-line {
        width: auto;
        padding: 0 2;
        content-align: right middle;
    }
    
    /* RunView styles */
    #progress-container {
        height: auto;
        padding: 1;
        background: $panel;
        border-bottom: solid $primary;
    }
    
    #run-title {
        text-style: bold;
        text-align: center;
    }
    
    #current-module {
        margin-top: 1;
    }
    
    #progress-bar {
        margin-top: 1;
    }
    
    #elapsed-time {
        text-align: right;
        color: $text-muted;
    }
    
    #log-viewer {
        margin: 1;
        padding: 1;
        border: solid $primary;
    }
    
    #footer-controls {
        height: auto;
        layout: horizontal;
        padding: 1;
        background: $panel;
        border-top: solid $primary;
    }
    
    #footer-controls Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
        Binding("ctrl+enter", "run", "Run", priority=True),
        Binding("r", "reset", "Reset"),
        Binding("a", "select_all", "Select All"),
        Binding("up", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("left", "collapse", "Collapse", show=False),
        Binding("right", "expand", "Expand", show=False),
        Binding("space", "toggle", "Toggle", show=False),
        Binding("enter", "toggle", "Toggle", show=False),
    ]
    
    def __init__(self) -> None:
        super().__init__()
        self.modules = self.initializeModules()
        self.dry_run = True
        self.create_timeshift = False
        self.recommended_daily = False
    
    def initializeModules(self) -> Dict[str, ModuleItem]:
        """Initialize module structure"""
        modules = {}
        
        # Define all modules with their metadata
        module_defs = [
            # System Maintenance
            ModuleItem("sys", "System Maintenance", "Core system maintenance tasks", children=["sys:timeshift", "sys:update_apt", "sys:manage_kernels", "sys:update_firmware", "sys:optimize_ssd"]),
            ModuleItem("sys:timeshift", "Create safety checkpoint (Timeshift)", "Create system restore point before changes", parent="sys"),
            ModuleItem("sys:update_apt", "Update APT core packages", "Update system packages via APT", parent="sys"),
            ModuleItem("sys:manage_kernels", "Manage old kernels", "Remove old kernel versions", parent="sys"),
            ModuleItem("sys:update_firmware", "Update device firmware", "Update hardware firmware", parent="sys"),
            ModuleItem("sys:optimize_ssd", "Optimize SSD", "Run SSD optimization tasks", parent="sys"),
            
            # Application Management
            ModuleItem("apps", "Application Management", "Manage installed applications", children=["apps:update_flatpak", "apps:update_snap", "apps:check_brew", "apps:update_python", "apps:scan_standalone"]),
            ModuleItem("apps:update_flatpak", "Update Flatpak apps", "Update all Flatpak applications", parent="apps"),
            ModuleItem("apps:update_snap", "Update Snap packages", "Update all Snap packages", parent="apps"),
            ModuleItem("apps:check_brew", "Check Homebrew tools", "Check for Homebrew updates", parent="apps"),
            ModuleItem("apps:update_python", "Update Python packages", "Update Python packages", parent="apps"),
            ModuleItem("apps:scan_standalone", "Detect standalone app updates", "Scan for standalone app updates", parent="apps"),
            
            # Cleanup Operations
            ModuleItem("clean", "Cleanup Operations", "System cleanup tasks", children=["clean:orphans", "clean:logs", "clean:docker", "clean:bleachbit", "clean:updatedb"]),
            ModuleItem("clean:orphans", "Remove orphaned packages", "Remove packages no longer needed", parent="clean"),
            ModuleItem("clean:logs", "Clean system logs", "Clear old system log files", parent="clean"),
            ModuleItem("clean:docker", "Clean Docker containers/images", "Remove unused Docker resources", parent="clean"),
            ModuleItem("clean:bleachbit", "Deep clean (BleachBit)", "Run BleachBit for deep cleaning", parent="clean"),
            ModuleItem("clean:updatedb", "Update file search database", "Update locate database", parent="clean"),
            
            # Health Checks
            ModuleItem("health", "Health Checks", "System health monitoring", children=["health:disk", "health:services", "health:gpu", "health:auto_updates"]),
            ModuleItem("health:disk", "Disk health", "Check disk health status", parent="health"),
            ModuleItem("health:services", "System services", "Check system service status", parent="health"),
            ModuleItem("health:gpu", "GPU status", "Check GPU health and drivers", parent="health"),
            ModuleItem("health:auto_updates", "Automatic updates enabled", "Verify auto-update configuration", parent="health"),
        ]
        
        for module in module_defs:
            modules[module.id] = module
        
        # Timeshift is disabled when dry-run is ON
        modules["sys:timeshift"].enabled = False
        
        return modules
    
    def compose(self) -> ComposeResult:
        """Build the UI"""
        yield Header(show_clock=True)
        
        # Settings panel (top)
        self.cbDryRun = Checkbox(label="Dry-run", value=True, id="set-dry-run")
        self.cbDryRun.disabled = False
        
        self.cbTimeshift = Checkbox(label="Create safety checkpoint (Timeshift)", value=False, id="set-timeshift")
        self.cbTimeshift.disabled = True  # disabled when dry-run ON
        
        # Put them in a thin horizontal bar
        settings_bar = Horizontal(
            self.cbDryRun,
            self.cbTimeshift,
            id="settings-bar",
            classes="bar",
        )
        yield settings_bar
        
        # Module list in a scroll container
        from textual.containers import VerticalScroll
        self.moduleScroll = VerticalScroll(id="module-scroll")
        # We'll mount the module tree into it
        yield self.moduleScroll
        
        # Actions footer (auto height)
        actions = Horizontal(
            Button("Run", id="btn-run", classes="primary"),
            Button("Reset", id="btn-reset"),
            Button("Quit", id="btn-quit"),
            Label("0 modules selected", id="status-line"),
            id="actions-bar",
            classes="bar",
        )
        yield actions
    
    def on_mount(self) -> None:
        """Initialize the app when mounted"""
        # Mount the module tree into the scroll container
        module_tree = ModuleTree(self.modules, id="module-tree")
        self.moduleScroll.mount(module_tree)
        self.updateStatusLine()
    
    @on(Checkbox.Changed, "#set-dry-run")
    def onDryRunChanged(self, event: Checkbox.Changed) -> None:
        """Handle dry-run checkbox change"""
        val = bool(event.value)
        self.dry_run = val
        
        # Enable/disable timeshift based on dry-run
        self.cbTimeshift.disabled = val
        
        # If dry-run turned ON and timeshift was ON, turn it off
        if val and self.cbTimeshift.value:
            self.cbTimeshift.value = False
        
        # Also update the module tree
        self.modules["sys:timeshift"].enabled = not val
        
        # Refresh the module tree to update visual state
        module_tree = self.query_one("#module-tree", ModuleTree)
        if "sys:timeshift" in module_tree.checkboxes:
            module_tree.checkboxes["sys:timeshift"].disabled = val
    
    @on(Checkbox.Changed, "#set-timeshift")
    def onTimeshiftChanged(self, event: Checkbox.Changed) -> None:
        """Handle Timeshift checkbox change"""
        self.create_timeshift = event.value
        self.modules["sys:timeshift"].checked = event.value
        
        # Update the module tree
        module_tree = self.query_one("#module-tree", ModuleTree)
        if "sys:timeshift" in module_tree.checkboxes:
            module_tree.checkboxes["sys:timeshift"].value = event.value
    
    
    @on(ModuleTree.ModuleChanged)
    def handleModuleChange(self, event: ModuleTree.ModuleChanged) -> None:
        """Handle module selection changes"""
        self.updateStatusLine()
    
    @on(Button.Pressed, "#btn-run")
    def onRun(self, event: Button.Pressed) -> None:
        """Handle run button"""
        self.actionRun()
    
    @on(Button.Pressed, "#btn-quit")
    def onQuit(self, event: Button.Pressed) -> None:
        """Handle quit button"""
        self.exit()
    
    @on(Button.Pressed, "#btn-reset")
    def onReset(self, event: Button.Pressed) -> None:
        """Handle reset button"""
        self.actionReset()
    
    def updateStatusLine(self) -> None:
        """Update the status line with selection count"""
        selected_count = sum(1 for m in self.modules.values() 
                           if m.checked and ":" in m.id)
        status = self.query_one("#status-line", Label)
        status.update(str(selected_count) + " modules selected")
    
    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()
    
    def actionRun(self) -> None:
        """Run selected modules"""
        # Collect selected modules
        selected = [m.id for m in self.modules.values() 
                   if m.checked and ":" in m.id]
        
        if not selected and not self.create_timeshift:
            self.notify("No modules selected", severity="warning")
            return
        
        # Create manifest
        manifest = {
            "dry_run": self.dry_run,
            "create_timeshift": self.create_timeshift,
            "selected": selected
        }
        
        # Write manifest to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(manifest, f, indent=2)
            manifest_path = f.name
        
        # Calculate total modules to run
        selected_count = len(selected)
        if self.create_timeshift:
            selected_count += 1
        
        # Push the RunView screen instead of exiting
        run_view = RunView(manifest_path, self.dry_run, selected_count)
        self.push_screen(run_view)
    
    def actionReset(self) -> None:
        """Reset to default state"""
        # Reset settings
        self.cbDryRun.value = True
        self.cbTimeshift.value = False
        self.cbTimeshift.disabled = True
        
        # Reset all modules
        module_tree = self.query_one("#module-tree", ModuleTree)
        for module in self.modules.values():
            module.checked = False
            if module.id in module_tree.checkboxes:
                module_tree.checkboxes[module.id].value = False
        
        self.updateStatusLine()
        self.notify("Reset to defaults", severity="information")
    
    def action_select_all(self) -> None:
        """Toggle select all modules"""
        module_tree = self.query_one("#module-tree", ModuleTree)
        
        # Check if any modules are selected
        any_selected = any(m.checked for m in self.modules.values() if ":" in m.id)
        
        # Toggle all
        for module in self.modules.values():
            if ":" in module.id and module.enabled:
                module.checked = not any_selected
                if module.id in module_tree.checkboxes:
                    module_tree.checkboxes[module.id].value = not any_selected
        
        self.updateStatusLine()


def main() -> None:
    """Main entry point"""
    app = MaintenanceTUI()
    app.run()


if __name__ == "__main__":
    main()

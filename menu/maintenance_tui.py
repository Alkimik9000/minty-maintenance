#!/usr/bin/env python3
"""
🍃 minty-maintenance Interactive TUI
Mouse-friendly, colorful maintenance module selector with tri-state checkboxes
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from textual import on
from textual.events import Click
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Checkbox, Header, Label, Static
from textual.message import Message


@dataclass
class ModuleItem:
    """Represents a maintenance module"""
    id: str
    label: str
    description: str
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    checked: bool = False
    expanded: bool = True
    enabled: bool = True


class TriStateCheckbox(Checkbox):
    """Checkbox that supports tri-state (checked, unchecked, partial)"""
    
    class Changed(Message):
        """Message sent when checkbox state changes"""
        def __init__(self, checkbox: "TriStateCheckbox", value: Optional[bool]) -> None:
            self.checkbox = checkbox
            self.value = value
            super().__init__()
    
    partial = reactive(False)
    
    def __init__(self, label: str = "", value: bool = False, *, 
                 id: Optional[str] = None, classes: Optional[str] = None,
                 disabled: bool = False) -> None:
        super().__init__(label, value, id=id, classes=classes, disabled=disabled)
        self.partial = False
    
    def renderLabel(self) -> str:
        """Render checkbox with tri-state support"""
        if self.partial:
            return "⧖ " + str(self.label)
        elif self.value:
            return "☑ " + str(self.label)
        else:
            return "☐ " + str(self.label)
    
    def toggle(self) -> None:
        """Toggle between states"""
        if not self.disabled:
            if self.partial:
                self.value = True
                self.partial = False
            else:
                self.value = not self.value
                self.partial = False
            self.post_message(self.Changed(self, self.value))


class ModuleTree(Widget):
    """Tree widget for module selection with collapsible groups"""
    
    def __init__(self, modules: Dict[str, ModuleItem], **kwargs) -> None:
        super().__init__(**kwargs)
        self.modules = modules
        self.checkboxes: Dict[str, TriStateCheckbox] = {}
        self.selected_module: Optional[str] = None
        self.group_expanded: Dict[str, bool] = {
            "sys": True,
            "apps": True, 
            "clean": True,
            "health": True
        }
    
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
                # Create group container
                with Container(classes="module-group") as group_container:
                    # Group header with expand/collapse
                    chevron = "▾" if self.group_expanded.get(group_id, True) else "▸"
                    yield Static(chevron + " " + group_label, 
                               classes="group-header", 
                               id="group-" + group_id)
                
                    # Group items container
                    with Container(classes="group-items", id="items-" + group_id) as items_container:
                        # Only show items if group is expanded
                        if self.group_expanded.get(group_id, True):
                            for item_id, item_label in items:
                                module = self.modules.get(item_id, ModuleItem(item_id, item_label, ""))
                                checkbox = TriStateCheckbox(
                                    item_label,
                                    value=module.checked,
                                    id="cb-" + item_id,
                                    classes="module-checkbox",
                                    disabled=not module.enabled
                                )
                                self.checkboxes[item_id] = checkbox
                                yield checkbox
                        else:
                            # Group is collapsed, hide items
                            items_container.display = False
    
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
    
    @on(TriStateCheckbox.Changed)
    def handleCheckboxChange(self, event: TriStateCheckbox.Changed) -> None:
        """Handle checkbox state changes"""
        checkbox_id = event.checkbox.id
        if checkbox_id and checkbox_id.startswith("cb-"):
            module_id = checkbox_id[3:]  # Remove "cb-" prefix
            if module_id in self.modules:
                self.modules[module_id].checked = event.value or False
                self.updateTriState(module_id)
                self.post_message(ModuleTree.ModuleChanged(module_id, event.value))
    
    class ModuleChanged(Message):
        """Message sent when a module selection changes"""
        def __init__(self, module_id: str, checked: Optional[bool]) -> None:
            self.module_id = module_id
            self.checked = checked
            super().__init__()
    
    def on_click(self, event) -> None:
        """Handle clicks on the widget"""
        # Get the widget that was clicked
        target = event.widget
        
        # Check if it's a group header by class
        if target and "group-header" in target.classes:
            if target.id and target.id.startswith("group-"):
                group_id = target.id[6:]  # Remove "group-" prefix
                
                # Toggle expansion state
                self.group_expanded[group_id] = not self.group_expanded.get(group_id, True)
                
                # Update chevron
                chevron = "▾" if self.group_expanded[group_id] else "▸"
                current_text = str(target.renderable) if hasattr(target, 'renderable') else target.render()
                group_label = current_text.split(" ", 1)[1] if " " in current_text else current_text
                target.update(chevron + " " + group_label)
                
                # Toggle visibility of items container
                items_container = self.query_one("#items-" + group_id, Container)
                items_container.display = self.group_expanded[group_id]


class MaintenanceTUI(App):
    """Main TUI application for minty-maintenance"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #header {
        height: 3;
        background: $primary;
        color: $text;
        padding: 1;
    }
    
    #settings-panel {
        height: 5;
        background: $panel;
        border: solid $primary;
        margin: 1;
        padding: 1;
    }
    
    #module-container {
        height: 1fr;
        background: $surface;
        border: solid $primary;
        margin: 0 1;
    }
    
    .module-group {
        margin: 0 1;
    }
    
    .group-header {
        padding: 1 0;
        color: $primary;
        text-style: bold;
    }
    
    .group-header:hover {
        background: $primary 20%;
    }
    
    .group-items {
        padding-left: 2;
    }
    
    .module-checkbox {
        height: 1;
        margin: 0;
        padding: 0 1;
    }
    
    .module-checkbox:hover {
        background: $primary 10%;
    }
    
    .module-checkbox:disabled {
        opacity: 50%;
    }
    
    #macro-panel {
        height: 3;
        background: $panel;
        border: solid $primary;
        margin: 0 1 1 1;
        padding: 1;
    }
    
    #footer-buttons {
        height: 3;
        background: $panel;
        align: center middle;
        padding: 0 2;
    }
    
    #footer-buttons Button {
        margin: 0 1;
        min-width: 10;
    }
    
    #status-line {
        height: 1;
        background: $surface;
        color: $text-muted;
        padding: 0 2;
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
        
        with Vertical():
            # Settings panel
            with Container(id="settings-panel"):
                with Horizontal():
                    yield Checkbox("Dry-run", value=True, id="dry-run-check")
                    yield Checkbox("Create safety checkpoint (Timeshift)", 
                                 value=False, 
                                 id="timeshift-check",
                                 disabled=True)
            
            # Module tree
            yield ModuleTree(self.modules, id="module-tree")
            
            # Macro panel
            with Container(id="macro-panel"):
                yield Checkbox("Recommended Daily", value=False, id="macro-daily")
            
            # Footer buttons
            with Horizontal(id="footer-buttons"):
                yield Button("Run", variant="success", id="run-btn")
                yield Button("Quit", variant="error", id="quit-btn")
                yield Button("Reset", variant="default", id="reset-btn")
            
            # Status line
            yield Label("0 modules selected", id="status-line")
    
    def on_mount(self) -> None:
        """Initialize the app when mounted"""
        self.updateStatusLine()
    
    @on(Checkbox.Changed, "#dry-run-check")
    def handleDryRunChange(self, event: Checkbox.Changed) -> None:
        """Handle dry-run checkbox change"""
        self.dry_run = event.value
        
        # Enable/disable Timeshift based on dry-run
        timeshift_check = self.query_one("#timeshift-check", Checkbox)
        timeshift_check.disabled = self.dry_run
        
        # Also update the module tree
        self.modules["sys:timeshift"].enabled = not self.dry_run
        
        # Refresh the module tree to update visual state
        module_tree = self.query_one("#module-tree", ModuleTree)
        if "sys:timeshift" in module_tree.checkboxes:
            module_tree.checkboxes["sys:timeshift"].disabled = self.dry_run
    
    @on(Checkbox.Changed, "#timeshift-check")
    def handleTimeshiftChange(self, event: Checkbox.Changed) -> None:
        """Handle Timeshift checkbox change"""
        self.create_timeshift = event.value
        self.modules["sys:timeshift"].checked = event.value
        
        # Update the module tree
        module_tree = self.query_one("#module-tree", ModuleTree)
        if "sys:timeshift" in module_tree.checkboxes:
            module_tree.checkboxes["sys:timeshift"].value = event.value
    
    @on(Checkbox.Changed, "#macro-daily")
    def handleMacroDaily(self, event: Checkbox.Changed) -> None:
        """Handle Recommended Daily macro"""
        self.recommended_daily = event.value
        
        if event.value:
            # Apply recommended daily settings
            # Turn dry-run OFF
            dry_run_check = self.query_one("#dry-run-check", Checkbox)
            dry_run_check.value = False
            
            # Set Timeshift ON
            timeshift_check = self.query_one("#timeshift-check", Checkbox)
            timeshift_check.value = True
            timeshift_check.disabled = False
            
            # Check specific modules
            daily_modules = [
                # All Application Management
                "apps:update_flatpak", "apps:update_snap", "apps:check_brew", 
                "apps:update_python", "apps:scan_standalone",
                # Selected others
                "sys:update_apt", "clean:orphans", "clean:logs", "clean:updatedb"
            ]
            
            module_tree = self.query_one("#module-tree", ModuleTree)
            for module_id in daily_modules:
                if module_id in self.modules:
                    self.modules[module_id].checked = True
                    if module_id in module_tree.checkboxes:
                        module_tree.checkboxes[module_id].value = True
        
        self.updateStatusLine()
    
    @on(ModuleTree.ModuleChanged)
    def handleModuleChange(self, event: ModuleTree.ModuleChanged) -> None:
        """Handle module selection changes"""
        self.updateStatusLine()
    
    @on(Button.Pressed, "#run-btn")
    def handleRun(self, event: Button.Pressed) -> None:
        """Handle run button"""
        self.actionRun()
    
    @on(Button.Pressed, "#quit-btn")
    def handleQuit(self, event: Button.Pressed) -> None:
        """Handle quit button"""
        self.exit()
    
    @on(Button.Pressed, "#reset-btn")
    def handleReset(self, event: Button.Pressed) -> None:
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
        
        # Exit TUI and run the bash script
        self.exit(result=manifest_path)
    
    def actionReset(self) -> None:
        """Reset to default state"""
        # Reset settings
        self.query_one("#dry-run-check", Checkbox).value = True
        self.query_one("#timeshift-check", Checkbox).value = False
        self.query_one("#macro-daily", Checkbox).value = False
        
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
    manifest_path = app.run()
    
    if manifest_path:
        # Run the bash script with the manifest
        script_path = Path(__file__).parent.parent / "mint-maintainer.sh"
        if script_path.exists():
            cmd = ["bash", str(script_path), "--manifest", manifest_path]
            subprocess.run(cmd)
        else:
            print("Error: mint-maintainer.sh not found at:", script_path)


if __name__ == "__main__":
    main()

"""
Live Progress Monitor for LEF Development
"""

import asyncio
import click
import signal
import atexit
import aiohttp
from datetime import datetime
from rich.live import Live
from rich.layout import Layout
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.style import Style
from ..models import TaskStatus, TaskPriority, EventType

API_BASE_URL = "http://localhost:8000"

# Interactive icons
ICONS = {
    'run': '▶️',
    'warning': '⚠️',
    'info': 'ℹ️',
    'success': '✅',
    'pending': '⏳',
    'blocked': '🚫',
    'edit': '✏️',
    'delete': '🗑️',
    'settings': '⚙️',
    'error': '❌',
}

class LEFMonitor:
    def __init__(self):
        self.console = Console()
        self.session = None
        
    async def initialize(self):
        """Initialize the monitor."""
        self.session = aiohttp.ClientSession(API_BASE_URL)
        
    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
        self.console.print("[yellow]Monitor shutdown complete[/yellow]")
        
    async def get_components(self):
        """Get all component states."""
        async with self.session.get("/system/components") as response:
            if response.status == 200:
                return await response.json()
            return []
            
    async def get_tasks(self, phase=None, status=None):
        """Get tasks with optional filtering."""
        params = {}
        if phase:
            params["phase"] = phase
        if status:
            params["status"] = status
            
        async with self.session.get("/tasks", params=params) as response:
            if response.status == 200:
                return await response.json()
            return []
            
    async def get_phase_progress(self, phase: str):
        """Get progress for a specific phase."""
        async with self.session.get(f"/tasks/phase/{phase}") as response:
            if response.status == 200:
                return await response.json()
            return {"progress_percentage": 0, "total_tasks": 0, "completed_tasks": 0}
            
    async def get_blocked_tasks(self):
        """Get all blocked tasks."""
        async with self.session.get("/tasks/blocked") as response:
            if response.status == 200:
                return await response.json()
            return []
            
    async def get_recent_events(self, limit=10):
        """Get recent system events."""
        async with self.session.get(f"/system/events?limit={limit}") as response:
            if response.status == 200:
                return await response.json()
            return []
            
    def create_status_table(self, components):
        """Create component status table."""
        table = Table(title="System Components")
        table.add_column("Component")
        table.add_column("Status")
        table.add_column("PID")
        table.add_column("Last Update")
        
        for comp in components:
            status_style = {
                "running": "green",
                "stopped": "red",
                "failed": "red bold",
                "starting": "yellow"
            }.get(comp["status"], "white")
            
            table.add_row(
                comp["component_name"],
                Text(comp["status"], style=status_style),
                str(comp["process_id"] or "N/A"),
                comp["metadata"].get("last_update", "N/A")
            )
            
        return table
        
    def create_tasks_table(self, tasks, show_phase=True):
        """Create tasks table."""
        table = Table(title="Development Tasks")
        if show_phase:
            table.add_column("Phase")
        table.add_column("Task")
        table.add_column("Status")
        table.add_column("Progress")
        table.add_column("Priority")
        
        for task in tasks:
            status_style = {
                TaskStatus.COMPLETED.value: "green",
                TaskStatus.IN_PROGRESS.value: "yellow",
                TaskStatus.BLOCKED.value: "red",
                TaskStatus.NOT_STARTED.value: "white"
            }.get(task["status"], "white")
            
            priority_style = {
                TaskPriority.HIGH.value: "red",
                TaskPriority.MEDIUM.value: "yellow",
                TaskPriority.LOW.value: "green"
            }.get(task["priority"], "white")
            
            row = []
            if show_phase:
                row.append(task["phase"])
            row.extend([
                task["name"],
                Text(task["status"], style=status_style),
                f"{task['progress']}%",
                Text(task["priority"], style=priority_style)
            ])
            table.add_row(*row)
            
        return table
        
    def create_events_panel(self, events):
        """Create events panel."""
        event_lines = []
        for event in events:
            timestamp = datetime.fromisoformat(event["created_at"]).strftime("%H:%M:%S")
            icon = {
                EventType.PROCESS_START.value: ICONS["run"],
                EventType.PROCESS_STOP.value: ICONS["warning"],
                EventType.SYSTEM_ERROR.value: ICONS["error"],
                EventType.SUPERVISOR_ACTION.value: ICONS["settings"]
            }.get(event["event_type"], ICONS["info"])
            
            event_lines.append(
                f"{timestamp} {icon} [{event['component_name']}] {event['message']}"
            )
            
        return Panel("\n".join(event_lines), title="Recent Events")
        
    async def update_display(self, live):
        """Update the display with current system state."""
        try:
            # Get current data
            components = await self.get_components()
            tasks = await self.get_tasks()
            events = await self.get_recent_events()
            blocked = await self.get_blocked_tasks()
            
            # Create layout
            layout = Layout()
            layout.split_column(
                Layout(name="upper"),
                Layout(name="lower")
            )
            layout["upper"].split_row(
                Layout(name="status"),
                Layout(name="tasks")
            )
            layout["lower"].split_row(
                Layout(name="blocked"),
                Layout(name="events")
            )
            
            # Fill layout
            layout["status"].update(self.create_status_table(components))
            layout["tasks"].update(self.create_tasks_table(tasks))
            layout["blocked"].update(
                Panel(self.create_tasks_table(blocked, show_phase=True), title="Blocked Tasks")
            )
            layout["events"].update(self.create_events_panel(events))
            
            # Update display
            live.update(layout)
            
        except Exception as e:
            self.console.print(f"[red]Error updating display: {e}[/red]")
            
    async def run(self):
        """Run the monitor."""
        await self.initialize()
        
        try:
            with Live(
                console=self.console,
                screen=True,
                refresh_per_second=4
            ) as live:
                while True:
                    await self.update_display(live)
                    await asyncio.sleep(0.25)  # 4 times per second
                    
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Shutting down...[/yellow]")
        finally:
            await self.cleanup()

@click.command()
def main():
    """Start the LEF live monitor."""
    try:
        asyncio.run(LEFMonitor().run())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main() 
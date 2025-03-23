"""
LEF System Dashboard
"""

import asyncio
from datetime import datetime
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich.text import Text
from rich import box
from rich.progress import ProgressBar

from ..core.sentinel_network import SentinelNetwork
from ..core.backup_manager import BackupManager

class Dashboard:
    def __init__(self):
        """Initialize the dashboard."""
        self.console = Console()
        self.sentinel = SentinelNetwork()
        self.backup_mgr = BackupManager()
        self.layout = Layout()
        
        # Configure layout
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1)
        )
        
        self.layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1),
        )
        
        self.layout["left"].split(
            Layout(name="system"),
            Layout(name="performance"),
        )
        
        self.layout["right"].split(
            Layout(name="alerts"),
            Layout(name="tasks"),
            Layout(name="backup", size=10),
        )
        
    def generate_header(self) -> Panel:
        """Generate header panel."""
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_row(
            Text("LEF System Dashboard", style="bold blue")
        )
        return Panel(grid, style="blue")
        
    def generate_system_panel(self, metrics: dict) -> Panel:
        """Generate system health panel."""
        if not metrics:
            return Panel("No metrics available", title="System Health")
            
        table = Table(box=box.ROUNDED, expand=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        
        # Add CPU usage with color
        cpu_style = "green"
        if metrics.get("cpu_usage", 0) > 70:
            cpu_style = "yellow"
        if metrics.get("cpu_usage", 0) > 85:
            cpu_style = "red"
        table.add_row(
            "CPU Usage",
            Text(f"{metrics.get('cpu_usage', 0):.1f}%", style=cpu_style)
        )
        
        # Add Memory usage with color
        mem_style = "green"
        if metrics.get("memory_usage", 0) > 70:
            mem_style = "yellow"
        if metrics.get("memory_usage", 0) > 85:
            mem_style = "red"
        table.add_row(
            "Memory Usage",
            Text(f"{metrics.get('memory_usage', 0):.1f}%", style=mem_style)
        )
        
        # Add Disk usage with color
        disk_style = "green"
        if metrics.get("disk_usage", 0) > 70:
            disk_style = "yellow"
        if metrics.get("disk_usage", 0) > 85:
            disk_style = "red"
        table.add_row(
            "Disk Usage",
            Text(f"{metrics.get('disk_usage', 0):.1f}%", style=disk_style)
        )
        
        # Add available memory in GB
        table.add_row(
            "Memory Available",
            f"{metrics.get('memory_available', 0):.1f} GB"
        )
        
        # Add free disk space in GB
        table.add_row(
            "Disk Free",
            f"{metrics.get('disk_free', 0):.1f} GB"
        )
        
        return Panel(table, title="System Health", border_style="blue")
        
    def generate_performance_panel(self, metrics: dict) -> Panel:
        """Generate performance metrics panel."""
        if not metrics:
            return Panel("No metrics available", title="Performance")
            
        table = Table(box=box.ROUNDED, expand=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        
        # CPU details
        cpu = metrics.get("cpu", {})
        table.add_row("CPU User", f"{cpu.get('user', 0):.1f}%")
        table.add_row("CPU System", f"{cpu.get('system', 0):.1f}%")
        table.add_row("CPU Idle", f"{cpu.get('idle', 0):.1f}%")
        table.add_row("CPU Frequency", f"{cpu.get('frequency', 0):.0f} MHz")
        
        # IO stats
        io = metrics.get("io", {})
        table.add_row(
            "Disk Read",
            f"{io.get('read_bytes', 0) / (1024*1024):.1f} MB"
        )
        table.add_row(
            "Disk Write",
            f"{io.get('write_bytes', 0) / (1024*1024):.1f} MB"
        )
        
        # Network stats
        net = metrics.get("network", {})
        table.add_row(
            "Network Sent",
            f"{net.get('bytes_sent', 0) / (1024*1024):.1f} MB"
        )
        table.add_row(
            "Network Recv",
            f"{net.get('bytes_recv', 0) / (1024*1024):.1f} MB"
        )
        
        return Panel(table, title="Performance", border_style="blue")
        
    def generate_alerts_panel(self, alerts: list) -> Panel:
        """Generate alerts panel."""
        if not alerts:
            return Panel("No active alerts", title="System Alerts")
            
        table = Table(box=box.ROUNDED, expand=True)
        table.add_column("Time", style="cyan")
        table.add_column("Level", style="yellow")
        table.add_column("Message")
        
        # Show last 5 alerts
        for alert in alerts[-5:]:
            timestamp = datetime.fromtimestamp(alert["timestamp"])
            time_str = timestamp.strftime("%H:%M:%S")
            level_style = "yellow" if alert["level"] == "warning" else "red"
            
            table.add_row(
                time_str,
                Text(alert["level"].upper(), style=level_style),
                alert["message"]
            )
            
        return Panel(table, title="System Alerts", border_style="red")
        
    def generate_tasks_panel(self, tasks: list = None) -> Panel:
        """Generate tasks panel."""
        if not tasks:
            tasks = []  # TODO: Get actual tasks
            
        table = Table(box=box.ROUNDED, expand=True)
        table.add_column("Task", style="cyan")
        table.add_column("Status", justify="right")
        
        for task in tasks:
            status_style = {
                "pending": "yellow",
                "running": "blue",
                "completed": "green",
                "failed": "red"
            }.get(task.get("status", ""), "white")
            
            table.add_row(
                task.get("name", "Unknown"),
                Text(task.get("status", "unknown"), style=status_style)
            )
            
        if not tasks:
            table.add_row("No active tasks", "")
            
        return Panel(table, title="Active Tasks", border_style="blue")
        
    def generate_backup_panel(self, backups: list = None) -> Panel:
        """Generate backup status panel."""
        if not backups:
            return Panel("No backups available", title="Backup Status")
            
        table = Table(box=box.ROUNDED, expand=True)
        table.add_column("Time", style="cyan", width=12)
        table.add_column("Type", style="blue", width=8)
        table.add_column("Status", justify="right", width=10)
        
        # Show last 3 backups
        for backup in backups[:3]:
            timestamp = datetime.strptime(backup["timestamp"], "%Y%m%d_%H%M%S")
            time_str = timestamp.strftime("%H:%M:%S")
            
            status_style = "green"
            status = "✓"
            
            if backup["reason"] == "automatic":
                backup_type = "Auto"
            else:
                backup_type = "Manual"
            
            table.add_row(
                time_str,
                backup_type,
                Text(status, style=status_style)
            )
            
        # Add next scheduled backup
        next_backup = datetime.fromtimestamp(
            self.backup_mgr._last_backup + self.backup_mgr.backup_interval
        ).strftime("%H:%M:%S")
        
        table.add_row("", "", "")
        table.add_row(
            next_backup,
            "Next",
            Text("⏰", style="yellow")
        )
            
        return Panel(table, title="Backup Status", border_style="blue")
        
    async def update(self) -> None:
        """Update all dashboard components."""
        # Update header
        self.layout["header"].update(self.generate_header())
        
        # Update system metrics
        health_metrics = self.sentinel.get_health_metrics()
        self.layout["system"].update(self.generate_system_panel(health_metrics))
        
        # Update performance metrics
        perf_metrics = self.sentinel.get_performance_metrics()
        self.layout["performance"].update(self.generate_performance_panel(perf_metrics))
        
        # Update alerts
        alerts = self.sentinel.get_security_alerts()
        self.layout["alerts"].update(self.generate_alerts_panel(alerts))
        
        # Update tasks
        self.layout["tasks"].update(self.generate_tasks_panel())
        
        # Update backup status
        backups = await self.backup_mgr.list_backups()
        self.layout["backup"].update(self.generate_backup_panel(backups))
        
    async def run(self) -> None:
        """Run the dashboard."""
        # Start sentinel network and backup manager
        await self.sentinel.start()
        asyncio.create_task(self.backup_mgr.start_auto_backup())
        
        try:
            with Live(self.layout, refresh_per_second=2, screen=True):
                while True:
                    await self.update()
                    await asyncio.sleep(0.5)
        except KeyboardInterrupt:
            await self.sentinel.stop()
        finally:
            await self.sentinel.stop()

async def main():
    """Run the dashboard."""
    dashboard = Dashboard()
    await dashboard.run()

if __name__ == "__main__":
    asyncio.run(main()) 
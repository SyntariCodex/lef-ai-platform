"""
CLI Interface for LEF Progress Tracking
"""

import click
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
from ..utils.progress_tracker import ProgressTracker

console = Console()

@click.group()
def cli():
    """LEF Development Progress Tracking CLI"""
    pass

@cli.command()
def status():
    """Show current development status"""
    tracker = ProgressTracker()
    report = tracker.generate_report()
    
    # Create status table
    table = Table(title="LEF Development Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Current Phase", report["current_phase"])
    table.add_row("Completion", f"{report['completion_percentage']:.1f}%")
    table.add_row("Tasks Completed", str(report["completed_tasks"]))
    table.add_row("Total Tasks", str(report["total_tasks"]))
    table.add_row("Blocked Tasks", str(report["blocked_tasks"]))
    
    console.print(table)
    
    # Show next tasks
    if report["next_tasks"]:
        next_tasks_table = Table(title="Next Tasks")
        next_tasks_table.add_column("Task", style="cyan")
        next_tasks_table.add_column("Priority", style="yellow")
        next_tasks_table.add_column("Risk Level", style="red")
        
        for task in report["next_tasks"]:
            next_tasks_table.add_row(
                task["task"],
                str(task["priority"]),
                task["risk_level"]
            )
        
        console.print(next_tasks_table)
    
    # Show blockers
    if report["blockers"]:
        blockers_table = Table(title="Blocked Tasks")
        blockers_table.add_column("Task", style="cyan")
        blockers_table.add_column("Blockers", style="red")
        
        for blocked in report["blockers"]:
            blockers_table.add_row(
                f"{blocked['phase']}: {blocked['task']}",
                "\n".join(blocked["blockers"])
            )
        
        console.print(blockers_table)

@cli.command()
@click.argument('phase')
@click.argument('task')
@click.option('--complete/--incomplete', default=True, help="Mark as complete or incomplete")
@click.option('--notes', help="Add notes about the task")
@click.option('--blockers', help="Comma-separated list of blockers")
def update(phase, task, complete, notes, blockers):
    """Update task status"""
    tracker = ProgressTracker()
    
    blockers_list = blockers.split(',') if blockers else None
    tracker.update_task_status(phase, task, complete, notes, blockers_list)
    
    console.print(f"Updated task: {task} in phase: {phase}")
    if complete:
        console.print("[green]Marked as complete[/green]")
    else:
        console.print("[yellow]Marked as incomplete[/yellow]")

@cli.command()
@click.argument('phase')
def predict(phase):
    """Predict completion date for a phase"""
    tracker = ProgressTracker()
    completion_date = tracker.predict_completion(phase)
    
    if completion_date:
        console.print(f"Predicted completion date for {phase}: {completion_date}")
    else:
        console.print("[yellow]Not enough data to make prediction[/yellow]")

@cli.command()
def report():
    """Generate detailed progress report"""
    tracker = ProgressTracker()
    report = tracker.generate_report()
    
    # Create rich panel with report
    content = [
        f"LEF Development Progress Report",
        f"Generated: {report['last_updated']}",
        "",
        f"Current Phase: {report['current_phase']}",
        f"Overall Progress: {report['completion_percentage']:.1f}%",
        f"Tasks Completed: {report['completed_tasks']}/{report['total_tasks']}",
        f"Blocked Tasks: {report['blocked_tasks']}",
        "",
        "Next Tasks:",
        *[f"- {task['task']} (Priority: {task['priority']}, Risk: {task['risk_level']})"
          for task in report["next_tasks"]],
        "",
        "Blockers:",
        *[f"- {blocked['task']}: {', '.join(blocked['blockers'])}"
          for blocked in report["blockers"]]
    ]
    
    panel = Panel("\n".join(content), title="Progress Report", border_style="cyan")
    console.print(panel)

if __name__ == "__main__":
    cli() 
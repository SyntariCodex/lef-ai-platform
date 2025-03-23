"""
LEF Backup CLI
Command-line interface for managing system backups
"""

import sys
import asyncio
import argparse
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import box
from rich.prompt import Confirm

from ..core.backup_manager import BackupManager

console = Console()

async def list_backups(backup_mgr: BackupManager):
    """List all available backups."""
    backups = await backup_mgr.list_backups()
    
    if not backups:
        console.print("[yellow]No backups found[/yellow]")
        return
    
    table = Table(box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Timestamp", style="blue")
    table.add_column("Type", style="green")
    table.add_column("Files", justify="right")
    
    for backup in backups:
        timestamp = datetime.strptime(backup["timestamp"], "%Y%m%d_%H%M%S")
        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        num_files = len(backup["state_files"])
        if backup["database"]:
            num_files += 1
            
        table.add_row(
            backup["id"],
            time_str,
            backup["reason"].capitalize(),
            str(num_files)
        )
    
    console.print(table)

async def create_backup(backup_mgr: BackupManager, reason: str):
    """Create a new backup."""
    with console.status("[bold blue]Creating backup..."):
        backup_id = await backup_mgr.create_backup(reason)
        
    if backup_id:
        console.print(f"[green]✓[/green] Backup created successfully: {backup_id}")
    else:
        console.print("[red]✗[/red] Failed to create backup", style="red")

async def restore_backup(backup_mgr: BackupManager, backup_id: str):
    """Restore from a backup."""
    # List backups first
    await list_backups(backup_mgr)
    
    # Confirm restoration
    if not Confirm.ask(
        f"\nAre you sure you want to restore from backup {backup_id}?",
        default=False
    ):
        return
    
    with console.status("[bold blue]Restoring backup..."):
        success = await backup_mgr.restore_backup(backup_id)
        
    if success:
        console.print(f"[green]✓[/green] Backup {backup_id} restored successfully")
    else:
        console.print(f"[red]✗[/red] Failed to restore backup {backup_id}", style="red")

async def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="LEF Backup Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available backups")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new backup")
    create_parser.add_argument(
        "-r", "--reason",
        default="manual",
        help="Reason for creating the backup"
    )
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore from a backup")
    restore_parser.add_argument(
        "backup_id",
        help="ID of the backup to restore"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    backup_mgr = BackupManager()
    
    try:
        if args.command == "list":
            await list_backups(backup_mgr)
        elif args.command == "create":
            await create_backup(backup_mgr, args.reason)
        elif args.command == "restore":
            await restore_backup(backup_mgr, args.backup_id)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="red")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 
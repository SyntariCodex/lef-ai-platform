"""
LEF Command Processor - Tag-based command execution
"""

import asyncio
import logging
from typing import Dict, Any, Callable, Awaitable
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

# Configure logging
logger = logging.getLogger(__name__)

class CommandProcessor:
    """Process tag-based commands for LEF system."""
    
    def __init__(self):
        """Initialize command processor."""
        self.console = Console()
        self.commands: Dict[str, Callable[..., Awaitable[None]]] = {}
        self.session = PromptSession()
        
        # Register built-in commands
        self.register_command("#help", self.show_help)
        self.register_command("#status", self.show_status)
        self.register_command("#task", self.handle_task)
        self.register_command("#system", self.handle_system)
        self.register_command("#log", self.show_logs)
        
    def register_command(self, tag: str, handler: Callable[..., Awaitable[None]]):
        """Register a new command handler."""
        self.commands[tag] = handler
        
    async def show_help(self, args: str = ""):
        """Show help information."""
        help_text = """
        Available Commands:
        #help           - Show this help message
        #status        - Show system status
        #task create   - Create a new task
        #task list     - List all tasks
        #task update   - Update a task
        #system start  - Start system components
        #system stop   - Stop system components
        #log show      - Show recent logs
        #log tail      - Follow logs in real-time
        """
        self.console.print(Panel(help_text, title="LEF Command Help"))
        
    async def show_status(self, args: str = ""):
        """Show system status."""
        # TODO: Implement actual status check
        status = {
            "supervisor": "running",
            "components": {
                "api": "running",
                "database": "connected"
            }
        }
        self.console.print(Panel.fit(
            "\n".join([f"{k}: {v}" for k, v in status.items()]),
            title="System Status"
        ))
        
    async def handle_task(self, args: str = ""):
        """Handle task-related commands."""
        if not args:
            await self.show_help("task")
            return
            
        cmd_parts = args.split()
        action = cmd_parts[0] if cmd_parts else ""
        
        if action == "create":
            # TODO: Implement task creation
            self.console.print("[green]Task created successfully[/green]")
        elif action == "list":
            # TODO: Implement task listing
            self.console.print(Panel("No tasks found", title="Tasks"))
        elif action == "update":
            # TODO: Implement task update
            self.console.print("[yellow]Task update not implemented[/yellow]")
            
    async def handle_system(self, args: str = ""):
        """Handle system-related commands."""
        if not args:
            await self.show_help("system")
            return
            
        cmd_parts = args.split()
        action = cmd_parts[0] if cmd_parts else ""
        
        if action == "start":
            # TODO: Implement system start
            self.console.print("[green]Starting system components...[/green]")
        elif action == "stop":
            # TODO: Implement system stop
            self.console.print("[yellow]Stopping system components...[/yellow]")
            
    async def show_logs(self, args: str = ""):
        """Show system logs."""
        if not args:
            await self.show_help("log")
            return
            
        cmd_parts = args.split()
        action = cmd_parts[0] if cmd_parts else ""
        
        if action == "show":
            # TODO: Implement log viewing
            self.console.print(Panel("No recent logs", title="System Logs"))
        elif action == "tail":
            # TODO: Implement log following
            self.console.print("[yellow]Log following not implemented[/yellow]")
            
    async def process_command(self, command: str):
        """Process a command string."""
        try:
            if not command.startswith("#"):
                self.console.print("[red]Commands must start with # (e.g., #help)[/red]")
                return
                
            parts = command.split(maxsplit=1)
            tag = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if tag in self.commands:
                await self.commands[tag](args)
            else:
                self.console.print(f"[red]Unknown command: {tag}[/red]")
                await self.show_help()
                
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self.console.print(f"[red]Error: {str(e)}[/red]")
            
    async def run(self):
        """Run the command processor."""
        # Create command completer
        completer = WordCompleter(list(self.commands.keys()) + [
            "#task create", "#task list", "#task update",
            "#system start", "#system stop",
            "#log show", "#log tail"
        ])
        
        self.console.print("[green]LEF Command Processor[/green]")
        self.console.print("Type #help for available commands")
        
        while True:
            try:
                command = await self.session.prompt_async(
                    "LEF> ",
                    completer=completer
                )
                if command.lower() in ("exit", "quit"):
                    break
                await self.process_command(command)
            except (EOFError, KeyboardInterrupt):
                break
            except Exception as e:
                logger.error(f"Error in command loop: {e}")
                self.console.print(f"[red]Error: {str(e)}[/red]")
                
async def main():
    """Run the command processor."""
    processor = CommandProcessor()
    await processor.run()

if __name__ == "__main__":
    asyncio.run(main()) 
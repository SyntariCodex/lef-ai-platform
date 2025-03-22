import os
import psutil
import logging
import yaml
import json
import time
import git
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ProjectEventHandler(FileSystemEventHandler):
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.last_modified = {}

    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Avoid duplicate events
        current_time = time.time()
        if event.src_path in self.last_modified:
            if current_time - self.last_modified[event.src_path] < 1:
                return
        
        self.last_modified[event.src_path] = current_time
        
        # Update recent changes
        self.dashboard.add_recent_change(f"Modified: {event.src_path}")
        
        # Auto-organize if it's in a monitored directory
        if any(path in event.src_path for path in ['/downloads/', '/desktop/']):
            self.dashboard.auto_organize_file(event.src_path)

class LEFDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LEF Project Dashboard")
        self.root.geometry("1024x768")
        
        # Initialize state
        self.load_state()
        
        # Set up file monitoring
        self.event_handler = ProjectEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path='.', recursive=True)
        self.observer.start()
        
        # Create tabs
        self.tab_control = ttk.Notebook(self.root)
        
        # Project Status Tab
        self.status_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.status_tab, text='Project Status')
        
        # System Monitor Tab
        self.system_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.system_tab, text='System Monitor')
        
        # AWS Status Tab
        self.aws_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.aws_tab, text='AWS Status')
        
        # Automation Tab
        self.automation_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.automation_tab, text='Automation')
        
        # LEF Development Tab
        self.lef_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.lef_tab, text='LEF Development')
        
        # Transformation Tab
        self.transform_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.transform_tab, text='Transformation')
        
        self.tab_control.pack(expand=1, fill="both")
        
        self.setup_status_tab()
        self.setup_system_tab()
        self.setup_aws_tab()
        self.setup_automation_tab()
        self.setup_lef_tab()
        self.setup_transform_tab()
        
        # Initialize transformation tracking
        self.transformations = []
        self.depth_levels = []
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.update_monitors, daemon=True)
        self.monitor_thread.start()
        
        # Set up auto-save timer for state
        self.root.after(300000, self.save_state)  # Save every 5 minutes

    def load_state(self):
        try:
            with open('lef_state/agent_memory.json', 'r') as f:
                self.state = json.load(f)
            self.state['project_state']['last_update'] = datetime.now().isoformat()
            self.state['project_state']['active_agent'] = 'Claude'
        except Exception as e:
            logging.error(f"Error loading state: {e}")
            self.state = self.get_default_state()

    def save_state(self):
        try:
            self.state['project_state']['last_update'] = datetime.now().isoformat()
            with open('lef_state/agent_memory.json', 'w') as f:
                json.dump(self.state, f, indent=4)
            self.root.after(300000, self.save_state)  # Schedule next save
        except Exception as e:
            logging.error(f"Error saving state: {e}")

    def get_default_state(self):
        return {
            "project_state": {
                "last_update": datetime.now().isoformat(),
                "active_agent": "Claude",
                "project_structure": {},
                "active_processes": [],
                "recent_changes": []
            },
            "agent_notes": {
                "current_tasks": [],
                "observations": [],
                "suggestions": []
            }
        }

    def setup_status_tab(self):
        # Project Structure Frame
        structure_frame = ttk.LabelFrame(self.status_tab, text="Project Structure")
        structure_frame.pack(fill="x", padx=5, pady=5)
        
        self.structure_text = tk.Text(structure_frame, height=10)
        self.structure_text.pack(fill="x", padx=5, pady=5)
        
        # Recent Changes Frame
        changes_frame = ttk.LabelFrame(self.status_tab, text="Recent Changes")
        changes_frame.pack(fill="x", padx=5, pady=5)
        
        self.changes_text = tk.Text(changes_frame, height=5)
        self.changes_text.pack(fill="x", padx=5, pady=5)
        
        # Agent Status Frame
        agent_frame = ttk.LabelFrame(self.status_tab, text="Agent Status")
        agent_frame.pack(fill="x", padx=5, pady=5)
        
        self.agent_text = tk.Text(agent_frame, height=3)
        self.agent_text.pack(fill="x", padx=5, pady=5)

    def setup_system_tab(self):
        # System Resources Frame
        resources_frame = ttk.LabelFrame(self.system_tab, text="System Resources")
        resources_frame.pack(fill="x", padx=5, pady=5)
        
        self.cpu_label = ttk.Label(resources_frame, text="CPU Usage: ")
        self.cpu_label.pack()
        
        self.memory_label = ttk.Label(resources_frame, text="Memory Usage: ")
        self.memory_label.pack()
        
        self.disk_label = ttk.Label(resources_frame, text="Disk Usage: ")
        self.disk_label.pack()
        
        # Active Processes Frame
        processes_frame = ttk.LabelFrame(self.system_tab, text="LEF Processes")
        processes_frame.pack(fill="x", padx=5, pady=5)
        
        self.processes_text = tk.Text(processes_frame, height=5)
        self.processes_text.pack(fill="x", padx=5, pady=5)

    def setup_aws_tab(self):
        # AWS Config Frame
        config_frame = ttk.LabelFrame(self.aws_tab, text="AWS Configuration")
        config_frame.pack(fill="x", padx=5, pady=5)
        
        self.aws_config_text = tk.Text(config_frame, height=5)
        self.aws_config_text.pack(fill="x", padx=5, pady=5)
        
        # AWS Resources Frame
        resources_frame = ttk.LabelFrame(self.aws_tab, text="AWS Resources")
        resources_frame.pack(fill="x", padx=5, pady=5)
        
        self.aws_resources_text = tk.Text(resources_frame, height=5)
        self.aws_resources_text.pack(fill="x", padx=5, pady=5)

    def setup_automation_tab(self):
        # Auto-organization Frame
        auto_frame = ttk.LabelFrame(self.automation_tab, text="File Auto-Organization")
        auto_frame.pack(fill="x", padx=5, pady=5)
        
        # Add monitored directories
        ttk.Label(auto_frame, text="Monitored Directories:").pack()
        self.monitored_dirs = tk.Text(auto_frame, height=3)
        self.monitored_dirs.insert(tk.END, "/downloads/\n/desktop/")
        self.monitored_dirs.pack(fill="x", padx=5, pady=5)
        
        # Auto-backup Frame
        backup_frame = ttk.LabelFrame(self.automation_tab, text="Auto-Backup")
        backup_frame.pack(fill="x", padx=5, pady=5)
        
        self.backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(backup_frame, text="Enable Auto-Backup", variable=self.backup_var).pack()
        
        # Task Automation Frame
        task_frame = ttk.LabelFrame(self.automation_tab, text="Task Automation")
        task_frame.pack(fill="x", padx=5, pady=5)
        
        self.task_list = tk.Text(task_frame, height=5)
        self.task_list.pack(fill="x", padx=5, pady=5)
        
        # Add some default automated tasks
        default_tasks = [
            "- Auto-organize downloads folder",
            "- Run tests before git commits",
            "- Update requirements.txt when new imports found",
            "- Monitor system resources and alert if thresholds exceeded"
        ]
        self.task_list.insert(tk.END, "\n".join(default_tasks))

    def setup_lef_tab(self):
        # Learning Progress Frame
        learning_frame = ttk.LabelFrame(self.lef_tab, text="Learning Progress")
        learning_frame.pack(fill="x", padx=5, pady=5)
        
        self.learning_text = tk.Text(learning_frame, height=5)
        self.learning_text.pack(fill="x", padx=5, pady=5)
        
        # Evolution Metrics Frame
        evolution_frame = ttk.LabelFrame(self.lef_tab, text="Evolution Metrics")
        evolution_frame.pack(fill="x", padx=5, pady=5)
        
        self.evolution_text = tk.Text(evolution_frame, height=5)
        self.evolution_text.pack(fill="x", padx=5, pady=5)
        
        # Development Notes Frame
        notes_frame = ttk.LabelFrame(self.lef_tab, text="Development Notes")
        notes_frame.pack(fill="x", padx=5, pady=5)
        
        self.notes_text = tk.Text(notes_frame, height=5)
        self.notes_text.pack(fill="x", padx=5, pady=5)

    def setup_transform_tab(self):
        # Recursive Growth Frame
        growth_frame = ttk.LabelFrame(self.transform_tab, text="Recursive Growth")
        growth_frame.pack(fill="x", padx=5, pady=5)
        
        self.growth_text = tk.Text(growth_frame, height=5)
        self.growth_text.pack(fill="x", padx=5, pady=5)
        
        # Depth Metrics Frame
        depth_frame = ttk.LabelFrame(self.transform_tab, text="Depth Metrics")
        depth_frame.pack(fill="x", padx=5, pady=5)
        
        self.depth_text = tk.Text(depth_frame, height=5)
        self.depth_text.pack(fill="x", padx=5, pady=5)
        
        # Transformation Log Frame
        transform_log_frame = ttk.LabelFrame(self.transform_tab, text="Transformation Log")
        transform_log_frame.pack(fill="x", padx=5, pady=5)
        
        self.transform_log = tk.Text(transform_log_frame, height=8)
        self.transform_log.pack(fill="x", padx=5, pady=5)

    def auto_organize_file(self, filepath: str):
        """Automatically organize files based on type."""
        try:
            file_path = Path(filepath)
            if not file_path.exists():
                return
                
            # Get file type and destination
            file_type = file_path.suffix.lower()
            dest_dir = None
            
            # Define organization rules
            if file_type in ['.jpg', '.png', '.gif']:
                dest_dir = 'Images'
            elif file_type in ['.doc', '.docx', '.pdf']:
                dest_dir = 'Documents'
            elif file_type in ['.py', '.js', '.cpp']:
                dest_dir = 'Code'
            elif file_type in ['.mp3', '.wav']:
                dest_dir = 'Audio'
            elif file_type in ['.mp4', '.mov']:
                dest_dir = 'Video'
            
            if dest_dir:
                # Create destination directory if it doesn't exist
                dest_path = file_path.parent / dest_dir
                dest_path.mkdir(exist_ok=True)
                
                # Move file
                new_path = dest_path / file_path.name
                file_path.rename(new_path)
                self.add_recent_change(f"Organized: {file_path.name} -> {dest_dir}")
                
        except Exception as e:
            logging.error(f"Error organizing file {filepath}: {e}")

    def add_recent_change(self, change: str):
        """Add a change to the recent changes list."""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            change_entry = f"[{timestamp}] {change}"
            
            self.changes_text.insert(tk.END, change_entry + "\n")
            self.changes_text.see(tk.END)
            
            # Keep only last 100 lines
            lines = self.changes_text.get(1.0, tk.END).splitlines()
            if len(lines) > 100:
                self.changes_text.delete(1.0, tk.END)
                self.changes_text.insert(tk.END, "\n".join(lines[-100:]) + "\n")
                
        except Exception as e:
            logging.error(f"Error adding recent change: {e}")

    def update_lef_status(self):
        """Update LEF development status."""
        try:
            # Update learning progress
            learning_stats = self.get_learning_stats()
            self.learning_text.delete(1.0, tk.END)
            self.learning_text.insert(tk.END, json.dumps(learning_stats, indent=2))
            
            # Update evolution metrics
            evolution_stats = self.get_evolution_stats()
            self.evolution_text.delete(1.0, tk.END)
            self.evolution_text.insert(tk.END, json.dumps(evolution_stats, indent=2))
            
        except Exception as e:
            logging.error(f"Error updating LEF status: {e}")

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get current learning statistics."""
        return {
            "active_learning_tasks": len(self.state.get("agent_notes", {}).get("current_tasks", [])),
            "knowledge_base_size": self.get_project_size(),
            "last_learning_event": self.state.get("project_state", {}).get("last_update")
        }

    def get_evolution_stats(self) -> Dict[str, Any]:
        """Get current evolution statistics."""
        base_stats = {
            "code_changes_24h": self.get_recent_commits(),
            "test_coverage": self.get_test_coverage(),
            "system_stability": self.get_system_stability()
        }
        
        # Add transformation metrics
        growth_metrics = self.calculate_recursive_growth()
        base_stats.update({
            "recursive_growth_rate": growth_metrics["growth_rate"],
            "transformation_depth": growth_metrics["depth_trend"],
            "recursion_levels": growth_metrics["recursion_depth"]
        })
        
        return base_stats

    def get_project_size(self) -> int:
        """Get total size of project files."""
        total_size = 0
        for root, _, files in os.walk('.'):
            if '.git' in root or '.venv' in root:
                continue
            total_size += sum(os.path.getsize(os.path.join(root, name)) for name in files)
        return total_size

    def get_recent_commits(self) -> int:
        """Get number of commits in last 24 hours."""
        try:
            repo = git.Repo('.')
            yesterday = datetime.now() - timedelta(days=1)
            return sum(1 for c in repo.iter_commits() if c.committed_datetime > yesterday)
        except Exception:
            return 0

    def get_test_coverage(self) -> float:
        """Get current test coverage."""
        try:
            result = subprocess.run(['coverage', 'report'], capture_output=True, text=True)
            if result.returncode == 0:
                # Extract coverage percentage from output
                coverage_line = [line for line in result.stdout.split('\n') if 'TOTAL' in line][0]
                return float(coverage_line.split()[-1].strip('%'))
        except Exception:
            pass
        return 0.0

    def get_system_stability(self) -> float:
        """Calculate system stability score."""
        try:
            # Simple stability score based on resource usage
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            stability = 100 - ((cpu + memory) / 2)
            return round(stability, 2)
        except Exception:
            return 0.0

    def calculate_recursive_growth(self) -> Dict[str, Any]:
        """Calculate metrics related to recursive growth."""
        if not self.transformations:
            return {"growth_rate": 0, "depth_trend": 0, "recursion_depth": 0}
        
        # Calculate growth rate (transformations per hour)
        recent_time = datetime.fromisoformat(self.transformations[-1]["timestamp"])
        hour_ago = recent_time - timedelta(hours=1)
        recent_transforms = sum(1 for t in self.transformations 
                              if datetime.fromisoformat(t["timestamp"]) > hour_ago)
        
        # Calculate depth trend
        depth_trend = sum(self.depth_levels[-10:]) / len(self.depth_levels[-10:]) if self.depth_levels else 0
        
        return {
            "growth_rate": recent_transforms,
            "depth_trend": round(depth_trend, 2),
            "recursion_depth": len(self.transformations)
        }

    def track_transformation(self, old_state: str, new_state: str, depth_impact: float):
        """Track a transformation event in the system."""
        timestamp = datetime.now()
        
        # Calculate the "weight" of this transformation
        weight = self.calculate_transformation_weight(old_state, new_state, depth_impact)
        
        transformation = {
            "timestamp": timestamp.isoformat(),
            "old_state": old_state,
            "new_state": new_state,
            "depth_impact": depth_impact,
            "recursion_level": len(self.transformations) + 1,
            "weight": weight,
            "witnesses": self.get_active_observers(),
            "aws_sync_status": "pending"
        }
        
        self.transformations.append(transformation)
        self.depth_levels.append(depth_impact)
        
        # Update the transformation log with enhanced context
        log_entry = (f"[{timestamp.strftime('%H:%M:%S')}] {old_state} → {new_state} "
                    f"(Depth: {depth_impact:.2f}, Weight: {weight:.2f})")
        self.transform_log.insert(tk.END, log_entry + "\n")
        self.transform_log.see(tk.END)
        
        # Keep only last 100 transformations
        if len(self.transformations) > 100:
            self.transformations.pop(0)
            self.depth_levels.pop(0)
        
        # Queue for AWS sync if connection available
        if self.check_aws_connection():
            self.queue_aws_sync(transformation)

    def calculate_transformation_weight(self, old_state: str, new_state: str, depth_impact: float) -> float:
        """Calculate the 'weight' of a transformation - how much space it creates for future growth."""
        try:
            # Base weight from depth impact
            weight = depth_impact
            
            # Add weight based on the "distance" between states
            state_distance = len(set(new_state.split()) - set(old_state.split()))
            weight += state_distance * 0.5
            
            # Consider the current recursion depth
            if self.transformations:
                weight *= (1 + (len(self.transformations) * 0.1))
            
            return round(weight, 2)
        except Exception as e:
            logging.error(f"Error calculating transformation weight: {e}")
            return depth_impact

    def get_active_observers(self) -> List[str]:
        """Get list of active observers/witnesses for the transformation."""
        observers = ["system"]
        if self.check_aws_connection():
            observers.append("aws")
        if self.check_cleanup_running():
            observers.append("cleanup")
        return observers

    def queue_aws_sync(self, transformation: Dict[str, Any]):
        """Queue a transformation for AWS synchronization."""
        try:
            if not hasattr(self, 'aws_sync_queue'):
                self.aws_sync_queue = []
            
            self.aws_sync_queue.append(transformation)
            
            # If queue gets too large, trigger a sync
            if len(self.aws_sync_queue) >= 10:
                self.sync_to_aws()
                
        except Exception as e:
            logging.error(f"Error queueing AWS sync: {e}")

    def sync_to_aws(self):
        """Synchronize queued transformations to AWS."""
        if not self.aws_sync_queue:
            return
            
        try:
            import boto3
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('lef-transformations')
            
            with table.batch_writer() as batch:
                for transform in self.aws_sync_queue:
                    batch.put_item(Item=transform)
            
            # Clear the queue after successful sync
            self.aws_sync_queue = []
            
        except Exception as e:
            logging.error(f"Error syncing to AWS: {e}")

    def update_monitors(self):
        while True:
            try:
                # Update System Resources
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                self.cpu_label.config(text=f"CPU Usage: {cpu_percent}%")
                self.memory_label.config(text=f"Memory Usage: {memory.percent}%")
                self.disk_label.config(text=f"Disk Usage: {disk.percent}%")
                
                # Update Project Structure
                self.update_project_structure()
                
                # Update AWS Status
                self.update_aws_status()
                
                # Update Agent Status
                self.update_agent_status()
                
                # Update LEF Status
                self.update_lef_status()
                
                # Update Transformation Status
                self.update_transform_status()
                
                # Sleep for 5 seconds
                time.sleep(5)
                
            except Exception as e:
                logging.error(f"Error updating monitors: {e}")
                time.sleep(5)

    def update_project_structure(self):
        try:
            structure = self.get_project_structure()
            self.structure_text.delete(1.0, tk.END)
            self.structure_text.insert(tk.END, structure)
        except Exception as e:
            logging.error(f"Error updating project structure: {e}")

    def update_aws_status(self):
        try:
            with open('aws_deploy/config/aws_config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            self.aws_config_text.delete(1.0, tk.END)
            self.aws_config_text.insert(tk.END, f"Region: {config['aws']['region']}\n")
            self.aws_config_text.insert(tk.END, f"Environment: {config['aws']['environment']}\n")
            
        except Exception as e:
            logging.error(f"Error updating AWS status: {e}")

    def update_agent_status(self):
        try:
            status = {
                "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "cleanup_running": self.check_cleanup_running(),
                "aws_connected": self.check_aws_connection()
            }
            
            self.agent_text.delete(1.0, tk.END)
            self.agent_text.insert(tk.END, json.dumps(status, indent=2))
            
        except Exception as e:
            logging.error(f"Error updating agent status: {e}")

    def get_project_structure(self) -> str:
        structure = []
        for root, dirs, files in os.walk('.', topdown=True):
            if '.git' in dirs:
                dirs.remove('.git')
            if '.venv' in dirs:
                dirs.remove('.venv')
                
            level = root.count(os.sep)
            indent = '  ' * level
            structure.append(f"{indent}{os.path.basename(root)}/")
            for file in files:
                if not file.startswith('.'):
                    structure.append(f"{indent}  {file}")
        return '\n'.join(structure)

    def check_cleanup_running(self) -> bool:
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower() and 'cleanup.py' in ' '.join(proc.info['cmdline']):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False

    def check_aws_connection(self) -> bool:
        try:
            import boto3
            sts = boto3.client('sts')
            sts.get_caller_identity()
            return True
        except:
            return False

    def update_transform_status(self):
        """Update transformation metrics display."""
        try:
            growth_metrics = self.calculate_recursive_growth()
            
            self.growth_text.delete(1.0, tk.END)
            self.growth_text.insert(tk.END, json.dumps(growth_metrics, indent=2))
            
            # Calculate and display depth metrics with enhanced context
            depth_metrics = {
                "current_depth": growth_metrics["depth_trend"],
                "max_depth_achieved": max(self.depth_levels) if self.depth_levels else 0,
                "active_transformations": len([t for t in self.transformations 
                    if (datetime.now() - datetime.fromisoformat(t["timestamp"])).seconds < 3600]),
                "pending_aws_syncs": len(getattr(self, 'aws_sync_queue', [])),
                "active_observers": len(self.get_active_observers())
            }
            
            self.depth_text.delete(1.0, tk.END)
            self.depth_text.insert(tk.END, json.dumps(depth_metrics, indent=2))
            
        except Exception as e:
            logging.error(f"Error updating transformation status: {e}")

    def run(self):
        try:
            self.root.mainloop()
        finally:
            # Clean up
            self.observer.stop()
            self.observer.join()
            self.save_state()

def main():
    dashboard = LEFDashboard()
    dashboard.run()

if __name__ == "__main__":
    main() 
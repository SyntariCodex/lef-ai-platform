from typing import Dict, Any, Optional
import os
import shutil
import json
import time
from datetime import datetime
import logging
from pathlib import Path
import threading
import schedule

class BackupService:
    def __init__(self, backup_dir: str = "backups"):
        self.logger = logging.getLogger(__name__)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        
        # Configure backup schedule
        self._configure_schedule()
        self.scheduler_thread.start()

    def _configure_schedule(self):
        """Configure backup schedule"""
        # Daily full backup at 2 AM
        schedule.every().day.at("02:00").do(self.create_full_backup)
        
        # Hourly incremental backup
        schedule.every().hour.do(self.create_incremental_backup)
        
        # Weekly cleanup of old backups
        schedule.every().sunday.at("03:00").do(self.cleanup_old_backups)

    def _run_scheduler(self):
        """Run the scheduler in background"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def create_full_backup(self) -> bool:
        """Create a full backup of the system"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"full_backup_{timestamp}"
            backup_path.mkdir(exist_ok=True)

            # Backup core components
            self._backup_directory("src/core", backup_path / "core")
            self._backup_directory("src/metrics", backup_path / "metrics")
            self._backup_directory("src/tests", backup_path / "tests")
            
            # Backup configuration files
            self._backup_configs(backup_path / "configs")
            
            # Backup metrics and state
            self._backup_metrics_and_state(backup_path / "state")
            
            # Create backup manifest
            self._create_manifest(backup_path, "full")
            
            self.logger.info(f"Full backup created at {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Full backup failed: {str(e)}")
            return False

    def create_incremental_backup(self) -> bool:
        """Create an incremental backup of changed files"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"incremental_backup_{timestamp}"
            backup_path.mkdir(exist_ok=True)

            # Get last backup time
            last_backup = self._get_last_backup_time()
            
            # Backup only changed files
            changed_files = self._find_changed_files(last_backup)
            for file_path in changed_files:
                rel_path = file_path.relative_to(Path.cwd())
                dest_path = backup_path / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)
            
            # Create backup manifest
            self._create_manifest(backup_path, "incremental", changed_files)
            
            self.logger.info(f"Incremental backup created at {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Incremental backup failed: {str(e)}")
            return False

    def _backup_directory(self, src_dir: str, dest_dir: Path):
        """Backup a directory"""
        src_path = Path(src_dir)
        if src_path.exists():
            shutil.copytree(src_path, dest_dir, dirs_exist_ok=True)

    def _backup_configs(self, dest_dir: Path):
        """Backup configuration files"""
        config_files = [
            "docker-compose.yml",
            "docker-compose.override.yml",
            "prometheus.yml",
            "grafana.ini"
        ]
        dest_dir.mkdir(exist_ok=True)
        for config in config_files:
            if Path(config).exists():
                shutil.copy2(config, dest_dir / config)

    def _backup_metrics_and_state(self, dest_dir: Path):
        """Backup metrics and state data"""
        dest_dir.mkdir(exist_ok=True)
        if Path("PROGRESS.md").exists():
            shutil.copy2("PROGRESS.md", dest_dir / "PROGRESS.md")
        
        # Backup any state files in .lef directory
        lef_dir = Path.home() / ".lef"
        if lef_dir.exists():
            shutil.copytree(lef_dir, dest_dir / ".lef", dirs_exist_ok=True)

    def _create_manifest(self, backup_path: Path, backup_type: str, changed_files: Optional[list] = None):
        """Create a backup manifest file"""
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "type": backup_type,
            "files": [],
            "size": 0
        }
        
        for item in backup_path.rglob("*"):
            if item.is_file():
                manifest["files"].append(str(item.relative_to(backup_path)))
                manifest["size"] += item.stat().st_size
        
        if changed_files:
            manifest["changed_files"] = [str(f) for f in changed_files]
        
        with open(backup_path / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

    def _get_last_backup_time(self) -> Optional[datetime]:
        """Get the timestamp of the last backup"""
        try:
            backups = sorted(self.backup_dir.glob("*_backup_*"))
            if not backups:
                return None
            
            last_backup = backups[-1]
            timestamp_str = last_backup.name.split("_backup_")[1]
            return datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        except Exception:
            return None

    def _find_changed_files(self, since: Optional[datetime]) -> list:
        """Find files changed since last backup"""
        if not since:
            return []
        
        changed = []
        for root, _, files in os.walk("."):
            for file in files:
                file_path = Path(root) / file
                if file_path.stat().st_mtime > since.timestamp():
                    changed.append(file_path)
        return changed

    def cleanup_old_backups(self, keep_days: int = 30) -> bool:
        """Clean up old backups"""
        try:
            cutoff = time.time() - (keep_days * 24 * 60 * 60)
            
            for backup in self.backup_dir.glob("*_backup_*"):
                if backup.stat().st_mtime < cutoff:
                    if backup.is_dir():
                        shutil.rmtree(backup)
                    else:
                        backup.unlink()
            
            self.logger.info(f"Cleaned up backups older than {keep_days} days")
            return True
        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {str(e)}")
            return False

    def shutdown(self):
        """Shutdown the backup service"""
        self.running = False
        self.scheduler_thread.join() 
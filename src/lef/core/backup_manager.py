"""
LEF Backup Manager
Handles system state persistence, backups, and restoration
"""

import os
import json
import shutil
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import aiosqlite
import aiofiles

class BackupManager:
    """Manages system backups and state persistence."""
    
    def __init__(self):
        """Initialize backup manager."""
        self.logger = logging.getLogger("lef.backup")
        
        # Set up paths
        self.lef_dir = Path.home() / ".lef"
        self.backup_dir = self.lef_dir / "backups"
        self.data_dir = self.lef_dir / "data"
        self.state_dir = self.lef_dir / "state"
        
        # Create directories
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        file_handler = logging.FileHandler(self.lef_dir / "logs" / "backup.log")
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        
        # Backup settings
        self.max_backups = 5  # Keep last 5 backups
        self.backup_interval = 3600  # Backup every hour
        self._last_backup = 0
        
    async def create_backup(self, reason: str = "manual") -> Optional[str]:
        """Create a new backup of the system state.
        
        Args:
            reason: Reason for creating the backup
            
        Returns:
            Backup ID if successful, None otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_id = f"backup_{timestamp}"
            backup_path = self.backup_dir / backup_id
            
            self.logger.info(f"Creating backup {backup_id} ({reason})")
            
            # Create backup directory
            backup_path.mkdir(parents=True)
            
            # Backup database
            db_path = self.data_dir / "lef.db"
            if db_path.exists():
                async with aiosqlite.connect(db_path) as db:
                    await db.backup(self.backup_dir / backup_id / "lef.db")
            
            # Backup state files
            state_files = {}
            for state_file in self.state_dir.glob("*.json"):
                async with aiofiles.open(state_file, 'r') as f:
                    content = await f.read()
                    state_files[state_file.name] = json.loads(content)
            
            # Write backup metadata
            metadata = {
                "id": backup_id,
                "timestamp": timestamp,
                "reason": reason,
                "state_files": list(state_files.keys()),
                "database": "lef.db" if db_path.exists() else None
            }
            
            async with aiofiles.open(backup_path / "metadata.json", 'w') as f:
                await f.write(json.dumps(metadata, indent=2))
            
            # Write state files
            for filename, content in state_files.items():
                async with aiofiles.open(backup_path / filename, 'w') as f:
                    await f.write(json.dumps(content, indent=2))
            
            await self._cleanup_old_backups()
            self._last_backup = datetime.now().timestamp()
            
            self.logger.info(f"Backup {backup_id} created successfully")
            return backup_id
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None
            
    async def restore_backup(self, backup_id: str) -> bool:
        """Restore system from a backup.
        
        Args:
            backup_id: ID of the backup to restore
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            backup_path = self.backup_dir / backup_id
            if not backup_path.exists():
                self.logger.error(f"Backup {backup_id} not found")
                return False
            
            self.logger.info(f"Restoring from backup {backup_id}")
            
            # Read backup metadata
            async with aiofiles.open(backup_path / "metadata.json", 'r') as f:
                content = await f.read()
                metadata = json.loads(content)
            
            # Restore database if it exists
            if metadata["database"]:
                db_backup = backup_path / "lef.db"
                if db_backup.exists():
                    # Stop any active database connections
                    # TODO: Implement proper database connection management
                    await asyncio.sleep(1)
                    
                    # Restore database
                    shutil.copy2(db_backup, self.data_dir / "lef.db")
            
            # Restore state files
            for state_file in metadata["state_files"]:
                async with aiofiles.open(backup_path / state_file, 'r') as f:
                    content = await f.read()
                    state_data = json.loads(content)
                    
                async with aiofiles.open(self.state_dir / state_file, 'w') as f:
                    await f.write(json.dumps(state_data, indent=2))
            
            self.logger.info(f"Backup {backup_id} restored successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore backup: {e}")
            return False
            
    async def list_backups(self) -> List[Dict]:
        """List available backups.
        
        Returns:
            List of backup metadata
        """
        try:
            backups = []
            for backup_dir in sorted(self.backup_dir.glob("backup_*")):
                try:
                    async with aiofiles.open(backup_dir / "metadata.json", 'r') as f:
                        content = await f.read()
                        metadata = json.loads(content)
                        backups.append(metadata)
                except Exception as e:
                    self.logger.warning(f"Failed to read backup {backup_dir}: {e}")
            
            return backups
            
        except Exception as e:
            self.logger.error(f"Failed to list backups: {e}")
            return []
            
    async def _cleanup_old_backups(self):
        """Remove old backups keeping only the most recent ones."""
        try:
            backups = await self.list_backups()
            if len(backups) > self.max_backups:
                # Sort by timestamp and remove oldest
                backups.sort(key=lambda x: x["timestamp"], reverse=True)
                for backup in backups[self.max_backups:]:
                    backup_path = self.backup_dir / backup["id"]
                    if backup_path.exists():
                        shutil.rmtree(backup_path)
                        self.logger.info(f"Removed old backup {backup['id']}")
                        
        except Exception as e:
            self.logger.error(f"Failed to cleanup old backups: {e}")
            
    async def should_backup(self) -> bool:
        """Check if it's time for a new backup."""
        return (datetime.now().timestamp() - self._last_backup) >= self.backup_interval
        
    async def start_auto_backup(self):
        """Start automatic backup process."""
        self.logger.info("Starting automatic backup process")
        while True:
            try:
                if await self.should_backup():
                    await self.create_backup("automatic")
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                self.logger.error(f"Auto-backup error: {e}")
                await asyncio.sleep(300) 
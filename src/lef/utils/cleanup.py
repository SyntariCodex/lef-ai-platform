import os
import shutil
import time
import yaml
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WorkspaceCleaner:
    def __init__(self, config_file: str = 'cleanup_config.yaml'):
        self.config_file = config_file
        self.load_config()

    def load_config(self) -> None:
        """Load or create configuration file."""
        default_config = {
            'directories': {
                'documentation/screenshots': ['*.png'],
                'documentation/rtf': ['*.rtf'],
                'documentation/logs': ['*.log'],
                'backups': ['Back Up*', 'Syntari Back Up', 'untitled folder'],
                'tests': ['test_*.py'],
                'config': ['*.yaml', '*.json'],
                'src': ['*.py'],
                'aws_deploy': ['aws_*.py'],
                'models': ['*model*.py', '*train*.py'],
                'data': ['*.csv', '*.data', '*.db']
            },
            'essential_files': [
                'README.md',
                'requirements.txt',
                'setup.py',
                '.gitignore',
                'LICENSE',
                'Dockerfile',
                'cleanup.py',
                'cleanup_config.yaml'
            ],
            'schedule': {
                'enabled': True,
                'interval_minutes': 60,
                'quiet_hours': {
                    'start': '23:00',
                    'end': '06:00'
                }
            },
            'backup': {
                'enabled': True,
                'max_backups': 5,
                'backup_dir': 'backups/auto'
            }
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
            else:
                self.config = default_config
                with open(self.config_file, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False)
                logger.info(f"Created default configuration file: {self.config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config = default_config

    def is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours."""
        now = datetime.now().time()
        start = datetime.strptime(self.config['schedule']['quiet_hours']['start'], '%H:%M').time()
        end = datetime.strptime(self.config['schedule']['quiet_hours']['end'], '%H:%M').time()
        
        if start <= end:
            return start <= now <= end
        else:  # Handle case where quiet hours span midnight
            return now >= start or now <= end

    def create_backup(self) -> None:
        """Create a backup of important files."""
        if not self.config['backup']['enabled']:
            return

        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.join(self.config['backup']['backup_dir'], timestamp)
            os.makedirs(backup_dir, exist_ok=True)

            # Copy essential files
            for file in self.config['essential_files']:
                if os.path.exists(file):
                    shutil.copy2(file, backup_dir)

            # Clean up old backups
            backup_root = self.config['backup']['backup_dir']
            backups = sorted([d for d in os.listdir(backup_root) if os.path.isdir(os.path.join(backup_root, d))])
            while len(backups) > self.config['backup']['max_backups']:
                oldest = os.path.join(backup_root, backups.pop(0))
                shutil.rmtree(oldest)
                logger.info(f"Removed old backup: {oldest}")

            logger.info(f"Created backup: {backup_dir}")
        except Exception as e:
            logger.error(f"Backup failed: {e}")

    def cleanup_workspace(self) -> None:
        """Clean up the workspace according to configuration."""
        try:
            # Create backup before cleaning
            self.create_backup()

            # Create directories and move files
            for dir_path, patterns in self.config['directories'].items():
                os.makedirs(dir_path, exist_ok=True)
                for pattern in patterns:
                    for item in Path('.').glob(pattern):
                        if item.is_file():
                            if item.name in self.config['essential_files']:
                                continue
                            try:
                                shutil.move(str(item), os.path.join(dir_path, item.name))
                                logger.info(f"Moved {item} to {dir_path}")
                            except Exception as e:
                                logger.error(f"Could not move {item}: {e}")
                        elif item.is_dir() and 'backup' in dir_path.lower():
                            try:
                                if not os.path.exists(os.path.join(dir_path, item.name)):
                                    shutil.move(str(item), os.path.join(dir_path, item.name))
                                    logger.info(f"Moved directory {item} to {dir_path}")
                            except Exception as e:
                                logger.error(f"Could not move directory {item}: {e}")

            # Clean up empty directories
            for item in Path('.').glob('*'):
                if item.is_dir() and not any(item.iterdir()):
                    try:
                        item.rmdir()
                        logger.info(f"Removed empty directory: {item}")
                    except Exception as e:
                        logger.error(f"Could not remove directory {item}: {e}")

            # Log essential files
            logger.info("\nEssential files in root directory:")
            for file in self.config['essential_files']:
                if os.path.exists(file):
                    logger.info(f"- {file}")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    def run_scheduled(self) -> None:
        """Run cleanup on a schedule."""
        logger.info("Starting scheduled cleanup service")
        
        while True:
            try:
                if not self.is_quiet_hours():
                    logger.info("Running scheduled cleanup")
                    self.cleanup_workspace()
                
                # Sleep for the configured interval
                interval = self.config['schedule']['interval_minutes'] * 60
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Cleanup service stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in cleanup service: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying

if __name__ == '__main__':
    cleaner = WorkspaceCleaner()
    if cleaner.config['schedule']['enabled']:
        cleaner.run_scheduled()
    else:
        cleaner.cleanup_workspace() 
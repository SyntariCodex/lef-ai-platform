#!/bin/bash

# Create timestamp for backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$HOME/.lef/backups"
PROJECT_DIR="$(pwd)"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create backup
echo "Creating backup at $BACKUP_DIR/lef_backup_$TIMESTAMP.tar.gz"
tar -czf "$BACKUP_DIR/lef_backup_$TIMESTAMP.tar.gz" \
    --exclude=".git" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="*.pyo" \
    --exclude="*.pyd" \
    --exclude=".Python" \
    --exclude="env" \
    --exclude="venv" \
    --exclude=".env" \
    --exclude=".venv" \
    --exclude=".pytest_cache" \
    --exclude=".coverage" \
    --exclude="htmlcov" \
    --exclude=".mypy_cache" \
    --exclude=".ruff_cache" \
    --exclude=".eggs" \
    --exclude="*.egg-info" \
    --exclude="dist" \
    --exclude="build" \
    --exclude=".tox" \
    --exclude=".idea" \
    --exclude=".vscode" \
    --exclude="*.swp" \
    --exclude="*.swo" \
    --exclude="*~" \
    "$PROJECT_DIR"

# Keep only the last 5 backups
cd "$BACKUP_DIR"
ls -t lef_backup_*.tar.gz | tail -n +6 | xargs -r rm --

echo "Backup complete!" 
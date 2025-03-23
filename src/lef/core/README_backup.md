# LEF Backup System

The LEF Backup System provides robust backup and restore functionality for the LEF Recursive Awareness System. It automatically manages system state persistence and allows for manual backup and restoration when needed.

## Features

- **Automatic Backups**: System state is automatically backed up every hour
- **Manual Backups**: Create backups on demand using the CLI
- **Backup Rotation**: Maintains the last 5 backups to optimize storage
- **State Persistence**: Backs up both database and state files
- **Dashboard Integration**: Monitor backup status in real-time
- **Shutdown Protection**: Creates automatic backup before system shutdown

## Directory Structure

Backups are stored in the `~/.lef/backups` directory with the following structure:

```
~/.lef/backups/
  ├── backup_20240301_123456/
  │   ├── metadata.json
  │   ├── lef.db
  │   └── state_files/
  └── backup_20240301_234567/
      ├── metadata.json
      ├── lef.db
      └── state_files/
```

## Command Line Interface

The backup system can be managed using the `backup_cli.py` tool:

### List Backups
```bash
python -m src.lef.cli.backup_cli list
```

### Create Manual Backup
```bash
python -m src.lef.cli.backup_cli create [-r REASON]
```

### Restore from Backup
```bash
python -m src.lef.cli.backup_cli restore BACKUP_ID
```

## Dashboard Integration

The backup status is displayed in the LEF Dashboard, showing:
- Last 3 backups with timestamps
- Next scheduled backup time
- Backup success indicators

## Automatic Backup Schedule

- Hourly backups
- Pre-shutdown backup
- Maximum of 5 backups retained
- Oldest backups automatically removed

## Backup Contents

Each backup includes:
1. SQLite database state
2. JSON state files
3. Metadata including:
   - Backup ID
   - Timestamp
   - Reason
   - File inventory

## Recovery Process

When restoring from a backup:
1. System displays available backups
2. User selects backup ID
3. System confirms restoration
4. Database and state files are restored
5. System restarts automatically

## Best Practices

1. Create manual backups before major changes
2. Use descriptive reasons for manual backups
3. Test restore process periodically
4. Monitor backup status in dashboard
5. Keep backup directory on reliable storage

## Troubleshooting

Common issues and solutions:

1. **Backup Creation Fails**
   - Check disk space
   - Verify write permissions
   - Check logs at `~/.lef/logs/backup.log`

2. **Restore Fails**
   - Ensure backup exists
   - Check file permissions
   - Verify backup integrity

3. **Missing Backups**
   - Check rotation settings
   - Verify backup schedule
   - Check disk space

## Security

- Backups are stored locally
- Access requires file system permissions
- Metadata is stored in JSON format
- No sensitive data in backup names 
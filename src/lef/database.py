"""
Database module for the LEF system.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

from .models.task import TaskStatus, TaskPriority, TaskCreate, TaskResponse

# Database path
DB_PATH = Path.home() / ".lef" / "data" / "lef.db"

def init_db():
    """Initialize the database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phase TEXT NOT NULL,
            description TEXT,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            progress REAL DEFAULT 0.0,
            estimated_hours REAL,
            error_log TEXT,
            task_metadata TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            resource_baseline TEXT,
            resource_current TEXT,
            alert_threshold REAL DEFAULT 7.5,
            pulse_checkpoint_interval INTEGER DEFAULT 3,
            last_pulse_check TIMESTAMP,
            observer_confirmation_required BOOLEAN DEFAULT 0,
            observer_confirmed BOOLEAN DEFAULT 0,
            requires_sync TEXT
        )
    """)
    
    # Create task dependencies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_dependencies (
            task_id INTEGER,
            dependency_id INTEGER,
            PRIMARY KEY (task_id, dependency_id),
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
            FOREIGN KEY (dependency_id) REFERENCES tasks (id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

def get_db():
    """Get a database connection."""
    return sqlite3.connect(DB_PATH)

def create_task(task: TaskCreate) -> TaskResponse:
    """Create a new task."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Convert task data to SQLite format
    task_data = {
        "name": task.name,
        "phase": task.phase,
        "description": task.description,
        "priority": task.priority,
        "status": TaskStatus.PENDING,
        "progress": 0.0,
        "estimated_hours": task.estimated_hours,
        "task_metadata": json.dumps(task.task_metadata or {}),
        "resource_baseline": json.dumps(task.resource_baseline or {}),
        "resource_current": json.dumps({}),
        "alert_threshold": task.alert_threshold,
        "pulse_checkpoint_interval": task.pulse_checkpoint_interval,
        "observer_confirmation_required": task.observer_confirmation_required,
        "observer_confirmed": False,
        "requires_sync": json.dumps(task.requires_sync or [])
    }
    
    # Insert task
    cursor.execute("""
        INSERT INTO tasks (
            name, phase, description, priority, status, progress,
            estimated_hours, task_metadata, resource_baseline, resource_current,
            alert_threshold, pulse_checkpoint_interval, observer_confirmation_required,
            observer_confirmed, requires_sync
        ) VALUES (
            :name, :phase, :description, :priority, :status, :progress,
            :estimated_hours, :task_metadata, :resource_baseline, :resource_current,
            :alert_threshold, :pulse_checkpoint_interval, :observer_confirmation_required,
            :observer_confirmed, :requires_sync
        )
    """, task_data)
    
    task_id = cursor.lastrowid
    
    # Get created task
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    
    conn.commit()
    conn.close()
    
    return _row_to_task(row)

def get_task(task_id: int) -> Optional[TaskResponse]:
    """Get a task by ID."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    return _row_to_task(row) if row else None

def get_tasks(
    skip: int = 0,
    limit: int = 100,
    phase: Optional[str] = None,
    status: Optional[TaskStatus] = None
) -> List[TaskResponse]:
    """Get tasks with optional filtering."""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    
    if phase:
        query += " AND phase = ?"
        params.append(phase)
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    conn.close()
    
    return [_row_to_task(row) for row in rows]

def update_task(task_id: int, task_data: Dict) -> Optional[TaskResponse]:
    """Update a task."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Convert task data to SQLite format
    update_data = {}
    for key, value in task_data.items():
        if isinstance(value, (dict, list)):
            update_data[key] = json.dumps(value)
        else:
            update_data[key] = value
    
    update_data["updated_at"] = datetime.utcnow()
    
    # Build update query
    set_clause = ", ".join(f"{k} = ?" for k in update_data.keys())
    query = f"UPDATE tasks SET {set_clause} WHERE id = ?"
    
    # Execute update
    cursor.execute(query, list(update_data.values()) + [task_id])
    
    if cursor.rowcount == 0:
        conn.close()
        return None
    
    # Get updated task
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    
    conn.commit()
    conn.close()
    
    return _row_to_task(row)

def delete_task(task_id: int) -> bool:
    """Delete a task."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return deleted

def _row_to_task(row: tuple) -> TaskResponse:
    """Convert a database row to a TaskResponse object."""
    return TaskResponse(
        id=row[0],
        name=row[1],
        phase=row[2],
        description=row[3],
        priority=TaskPriority(row[4]),
        status=TaskStatus(row[5]),
        progress=row[6],
        estimated_hours=row[7],
        error_log=row[8],
        task_metadata=json.loads(row[9]) if row[9] else {},
        created_at=datetime.fromisoformat(row[10]),
        updated_at=datetime.fromisoformat(row[11]),
        started_at=datetime.fromisoformat(row[12]) if row[12] else None,
        completed_at=datetime.fromisoformat(row[13]) if row[13] else None,
        resource_baseline=json.loads(row[14]) if row[14] else {},
        resource_current=json.loads(row[15]) if row[15] else {},
        alert_threshold=row[16],
        pulse_checkpoint_interval=row[17],
        last_pulse_check=datetime.fromisoformat(row[18]) if row[18] else None,
        observer_confirmation_required=bool(row[19]),
        observer_confirmed=bool(row[20]),
        requires_sync=json.loads(row[21]) if row[21] else []
    ) 
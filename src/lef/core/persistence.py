"""
LEF Data Persistence Layer
Handles data storage, retrieval, and management across the system
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json
import yaml
import sqlite3
import logging
from datetime import datetime
import threading
from contextlib import contextmanager

class DataStore:
    """Core data persistence manager"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.home() / ".lef/data"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.base_path / "lef.db"
        self.logger = logging.getLogger("LEF.DataStore")
        self._lock = threading.Lock()
        self._initialize_db()

    def _initialize_db(self):
        """Initialize SQLite database with required tables"""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS system_state (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL,
                    labels TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);
                CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(name);
            """)

    @contextmanager
    def _get_connection(self):
        """Get a database connection with automatic cleanup"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def store_state(self, key: str, value: Any):
        """Store system state"""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO system_state (key, value, updated_at) VALUES (?, ?, ?)",
                        (key, json.dumps(value), datetime.now().isoformat())
                    )
                self.logger.debug(f"Stored state: {key}")
            except Exception as e:
                self.logger.error(f"Failed to store state {key}: {e}")
                raise

    def get_state(self, key: str, default: Any = None) -> Any:
        """Retrieve system state"""
        try:
            with self._get_connection() as conn:
                result = conn.execute(
                    "SELECT value FROM system_state WHERE key = ?",
                    (key,)
                ).fetchone()
                
                if result:
                    return json.loads(result[0])
                return default
        except Exception as e:
            self.logger.error(f"Failed to get state {key}: {e}")
            return default

    def record_event(self, event_type: str, data: Optional[Dict] = None):
        """Record system event"""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO events (type, data) VALUES (?, ?)",
                    (event_type, json.dumps(data) if data else None)
                )
            self.logger.debug(f"Recorded event: {event_type}")
        except Exception as e:
            self.logger.error(f"Failed to record event {event_type}: {e}")
            raise

    def get_events(
        self,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Retrieve system events"""
        query = "SELECT * FROM events"
        params = []
        
        if event_type or start_time:
            query += " WHERE"
            if event_type:
                query += " type = ?"
                params.append(event_type)
            if start_time:
                query += " AND" if event_type else ""
                query += " timestamp >= ?"
                params.append(start_time.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        try:
            with self._get_connection() as conn:
                results = conn.execute(query, params).fetchall()
                return [{
                    'id': row['id'],
                    'type': row['type'],
                    'data': json.loads(row['data']) if row['data'] else None,
                    'timestamp': row['timestamp']
                } for row in results]
        except Exception as e:
            self.logger.error(f"Failed to get events: {e}")
            return []

    def store_metric(self, name: str, value: float, labels: Optional[Dict] = None):
        """Store system metric"""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO metrics (name, value, labels) VALUES (?, ?, ?)",
                    (name, value, json.dumps(labels) if labels else None)
                )
            self.logger.debug(f"Stored metric: {name}={value}")
        except Exception as e:
            self.logger.error(f"Failed to store metric {name}: {e}")
            raise

    def get_metrics(
        self,
        name: str,
        start_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Retrieve system metrics"""
        query = "SELECT * FROM metrics WHERE name = ?"
        params = [name]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        try:
            with self._get_connection() as conn:
                results = conn.execute(query, params).fetchall()
                return [{
                    'id': row['id'],
                    'name': row['name'],
                    'value': row['value'],
                    'labels': json.loads(row['labels']) if row['labels'] else None,
                    'timestamp': row['timestamp']
                } for row in results]
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {e}")
            return []

    def cleanup_old_data(self, days: int = 30):
        """Clean up old data"""
        try:
            cutoff = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ).timestamp() - (days * 86400)
            
            with self._get_connection() as conn:
                conn.executescript(f"""
                    DELETE FROM events WHERE timestamp < {cutoff};
                    DELETE FROM metrics WHERE timestamp < {cutoff};
                    VACUUM;
                """)
            self.logger.info(f"Cleaned up data older than {days} days")
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            raise

# Global instance
store = DataStore() 
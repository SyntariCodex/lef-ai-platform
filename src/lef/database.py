"""
Database module for the LEF system.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

from .models.task import TaskStatus, TaskPriority, TaskCreate, TaskResponse
from .models.system_state import SystemState, SystemStatus, ComponentStatus

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
    
    # Create system state table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_state (
            id INTEGER PRIMARY KEY DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'initializing',
            last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            components TEXT,
            metrics TEXT,
            errors TEXT,
            warnings TEXT,
            metadata TEXT,
            version TEXT NOT NULL DEFAULT '1.0.0',
            uptime REAL DEFAULT 0.0,
            last_backup TIMESTAMP,
            last_sync TIMESTAMP,
            active_tasks INTEGER DEFAULT 0,
            pending_tasks INTEGER DEFAULT 0,
            failed_tasks INTEGER DEFAULT 0,
            completed_tasks INTEGER DEFAULT 0,
            resource_usage TEXT,
            performance_metrics TEXT,
            security_status TEXT,
            last_health_check TIMESTAMP,
            last_maintenance TIMESTAMP,
            maintenance_mode BOOLEAN DEFAULT 0,
            emergency_mode BOOLEAN DEFAULT 0,
            last_error TEXT,
            error_count INTEGER DEFAULT 0,
            warning_count INTEGER DEFAULT 0,
            last_alert TIMESTAMP,
            alert_count INTEGER DEFAULT 0,
            system_load REAL DEFAULT 0.0,
            memory_usage REAL DEFAULT 0.0,
            cpu_usage REAL DEFAULT 0.0,
            disk_usage REAL DEFAULT 0.0,
            network_status TEXT,
            last_network_check TIMESTAMP,
            active_connections INTEGER DEFAULT 0,
            pending_connections INTEGER DEFAULT 0,
            failed_connections INTEGER DEFAULT 0,
            last_connection_error TEXT,
            connection_error_count INTEGER DEFAULT 0,
            last_successful_operation TIMESTAMP,
            operation_success_rate REAL DEFAULT 0.0,
            last_failed_operation TIMESTAMP,
            operation_failure_rate REAL DEFAULT 0.0,
            last_recovery TIMESTAMP,
            recovery_count INTEGER DEFAULT 0,
            last_optimization TIMESTAMP,
            optimization_status TEXT,
            last_cleanup TIMESTAMP,
            cleanup_status TEXT,
            last_update TIMESTAMP,
            update_status TEXT,
            last_backup_size INTEGER,
            backup_status TEXT,
            last_sync_size INTEGER,
            sync_status TEXT,
            last_validation TIMESTAMP,
            validation_status TEXT,
            last_integrity_check TIMESTAMP,
            integrity_status TEXT,
            last_security_scan TIMESTAMP,
            security_scan_status TEXT,
            last_performance_test TIMESTAMP,
            performance_test_status TEXT,
            last_load_test TIMESTAMP,
            load_test_status TEXT,
            last_stress_test TIMESTAMP,
            stress_test_status TEXT,
            last_reliability_test TIMESTAMP,
            reliability_test_status TEXT,
            last_compatibility_test TIMESTAMP,
            compatibility_test_status TEXT,
            last_regression_test TIMESTAMP,
            regression_test_status TEXT,
            last_unit_test TIMESTAMP,
            unit_test_status TEXT,
            last_integration_test TIMESTAMP,
            integration_test_status TEXT,
            last_system_test TIMESTAMP,
            system_test_status TEXT,
            last_acceptance_test TIMESTAMP,
            acceptance_test_status TEXT,
            last_user_test TIMESTAMP,
            user_test_status TEXT,
            last_alpha_test TIMESTAMP,
            alpha_test_status TEXT,
            last_beta_test TIMESTAMP,
            beta_test_status TEXT,
            last_gamma_test TIMESTAMP,
            gamma_test_status TEXT,
            last_delta_test TIMESTAMP,
            delta_test_status TEXT,
            last_epsilon_test TIMESTAMP,
            epsilon_test_status TEXT,
            last_zeta_test TIMESTAMP,
            zeta_test_status TEXT,
            last_eta_test TIMESTAMP,
            eta_test_status TEXT,
            last_theta_test TIMESTAMP,
            theta_test_status TEXT,
            last_iota_test TIMESTAMP,
            iota_test_status TEXT,
            last_kappa_test TIMESTAMP,
            kappa_test_status TEXT,
            last_lambda_test TIMESTAMP,
            lambda_test_status TEXT,
            last_mu_test TIMESTAMP,
            mu_test_status TEXT,
            last_nu_test TIMESTAMP,
            nu_test_status TEXT,
            last_xi_test TIMESTAMP,
            xi_test_status TEXT,
            last_omicron_test TIMESTAMP,
            omicron_test_status TEXT,
            last_pi_test TIMESTAMP,
            pi_test_status TEXT,
            last_rho_test TIMESTAMP,
            rho_test_status TEXT,
            last_sigma_test TIMESTAMP,
            sigma_test_status TEXT,
            last_tau_test TIMESTAMP,
            tau_test_status TEXT,
            last_upsilon_test TIMESTAMP,
            upsilon_test_status TEXT,
            last_phi_test TIMESTAMP,
            phi_test_status TEXT,
            last_chi_test TIMESTAMP,
            chi_test_status TEXT,
            last_psi_test TIMESTAMP,
            psi_test_status TEXT,
            last_omega_test TIMESTAMP,
            omega_test_status TEXT
        )
    """)
    
    # Insert initial system state if not exists
    cursor.execute("SELECT COUNT(*) FROM system_state")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO system_state (
                id, status, version, last_updated
            ) VALUES (
                1, 'initializing', '1.0.0', CURRENT_TIMESTAMP
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

def get_system_state() -> SystemState:
    """Get the current system state."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM system_state WHERE id = 1")
    row = cursor.fetchone()
    
    conn.close()
    
    if not row:
        return SystemState()
    
    return _row_to_system_state(row)

def update_system_state(state: SystemState) -> SystemState:
    """Update the system state."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Convert state to SQLite format
    state_data = {
        "status": state.status.value,
        "last_updated": datetime.utcnow(),
        "components": json.dumps(state.components),
        "metrics": json.dumps(state.metrics),
        "errors": json.dumps(state.errors),
        "warnings": json.dumps(state.warnings),
        "metadata": json.dumps(state.metadata),
        "version": state.version,
        "uptime": state.uptime,
        "last_backup": state.last_backup,
        "last_sync": state.last_sync,
        "active_tasks": state.active_tasks,
        "pending_tasks": state.pending_tasks,
        "failed_tasks": state.failed_tasks,
        "completed_tasks": state.completed_tasks,
        "resource_usage": json.dumps(state.resource_usage),
        "performance_metrics": json.dumps(state.performance_metrics),
        "security_status": json.dumps(state.security_status),
        "last_health_check": state.last_health_check,
        "last_maintenance": state.last_maintenance,
        "maintenance_mode": state.maintenance_mode,
        "emergency_mode": state.emergency_mode,
        "last_error": state.last_error,
        "error_count": state.error_count,
        "warning_count": state.warning_count,
        "last_alert": state.last_alert,
        "alert_count": state.alert_count,
        "system_load": state.system_load,
        "memory_usage": state.memory_usage,
        "cpu_usage": state.cpu_usage,
        "disk_usage": state.disk_usage,
        "network_status": json.dumps(state.network_status),
        "last_network_check": state.last_network_check,
        "active_connections": state.active_connections,
        "pending_connections": state.pending_connections,
        "failed_connections": state.failed_connections,
        "last_connection_error": state.last_connection_error,
        "connection_error_count": state.connection_error_count,
        "last_successful_operation": state.last_successful_operation,
        "operation_success_rate": state.operation_success_rate,
        "last_failed_operation": state.last_failed_operation,
        "operation_failure_rate": state.operation_failure_rate,
        "last_recovery": state.last_recovery,
        "recovery_count": state.recovery_count,
        "last_optimization": state.last_optimization,
        "optimization_status": json.dumps(state.optimization_status),
        "last_cleanup": state.last_cleanup,
        "cleanup_status": json.dumps(state.cleanup_status),
        "last_update": state.last_update,
        "update_status": json.dumps(state.update_status),
        "last_backup_size": state.last_backup_size,
        "backup_status": json.dumps(state.backup_status),
        "last_sync_size": state.last_sync_size,
        "sync_status": json.dumps(state.sync_status),
        "last_validation": state.last_validation,
        "validation_status": json.dumps(state.validation_status),
        "last_integrity_check": state.last_integrity_check,
        "integrity_status": json.dumps(state.integrity_status),
        "last_security_scan": state.last_security_scan,
        "security_scan_status": json.dumps(state.security_scan_status),
        "last_performance_test": state.last_performance_test,
        "performance_test_status": json.dumps(state.performance_test_status),
        "last_load_test": state.last_load_test,
        "load_test_status": json.dumps(state.load_test_status),
        "last_stress_test": state.last_stress_test,
        "stress_test_status": json.dumps(state.stress_test_status),
        "last_reliability_test": state.last_reliability_test,
        "reliability_test_status": json.dumps(state.reliability_test_status),
        "last_compatibility_test": state.last_compatibility_test,
        "compatibility_test_status": json.dumps(state.compatibility_test_status),
        "last_regression_test": state.last_regression_test,
        "regression_test_status": json.dumps(state.regression_test_status),
        "last_unit_test": state.last_unit_test,
        "unit_test_status": json.dumps(state.unit_test_status),
        "last_integration_test": state.last_integration_test,
        "integration_test_status": json.dumps(state.integration_test_status),
        "last_system_test": state.last_system_test,
        "system_test_status": json.dumps(state.system_test_status),
        "last_acceptance_test": state.last_acceptance_test,
        "acceptance_test_status": json.dumps(state.acceptance_test_status),
        "last_user_test": state.last_user_test,
        "user_test_status": json.dumps(state.user_test_status),
        "last_alpha_test": state.last_alpha_test,
        "alpha_test_status": json.dumps(state.alpha_test_status),
        "last_beta_test": state.last_beta_test,
        "beta_test_status": json.dumps(state.beta_test_status),
        "last_gamma_test": state.last_gamma_test,
        "gamma_test_status": json.dumps(state.gamma_test_status),
        "last_delta_test": state.last_delta_test,
        "delta_test_status": json.dumps(state.delta_test_status),
        "last_epsilon_test": state.last_epsilon_test,
        "epsilon_test_status": json.dumps(state.epsilon_test_status),
        "last_zeta_test": state.last_zeta_test,
        "zeta_test_status": json.dumps(state.zeta_test_status),
        "last_eta_test": state.last_eta_test,
        "eta_test_status": json.dumps(state.eta_test_status),
        "last_theta_test": state.last_theta_test,
        "theta_test_status": json.dumps(state.theta_test_status),
        "last_iota_test": state.last_iota_test,
        "iota_test_status": json.dumps(state.iota_test_status),
        "last_kappa_test": state.last_kappa_test,
        "kappa_test_status": json.dumps(state.kappa_test_status),
        "last_lambda_test": state.last_lambda_test,
        "lambda_test_status": json.dumps(state.lambda_test_status),
        "last_mu_test": state.last_mu_test,
        "mu_test_status": json.dumps(state.mu_test_status),
        "last_nu_test": state.last_nu_test,
        "nu_test_status": json.dumps(state.nu_test_status),
        "last_xi_test": state.last_xi_test,
        "xi_test_status": json.dumps(state.xi_test_status),
        "last_omicron_test": state.last_omicron_test,
        "omicron_test_status": json.dumps(state.omicron_test_status),
        "last_pi_test": state.last_pi_test,
        "pi_test_status": json.dumps(state.pi_test_status),
        "last_rho_test": state.last_rho_test,
        "rho_test_status": json.dumps(state.rho_test_status),
        "last_sigma_test": state.last_sigma_test,
        "sigma_test_status": json.dumps(state.sigma_test_status),
        "last_tau_test": state.last_tau_test,
        "tau_test_status": json.dumps(state.tau_test_status),
        "last_upsilon_test": state.last_upsilon_test,
        "upsilon_test_status": json.dumps(state.upsilon_test_status),
        "last_phi_test": state.last_phi_test,
        "phi_test_status": json.dumps(state.phi_test_status),
        "last_chi_test": state.last_chi_test,
        "chi_test_status": json.dumps(state.chi_test_status),
        "last_psi_test": state.last_psi_test,
        "psi_test_status": json.dumps(state.psi_test_status),
        "last_omega_test": state.last_omega_test,
        "omega_test_status": json.dumps(state.omega_test_status)
    }
    
    # Build update query
    set_clause = ", ".join(f"{k} = ?" for k in state_data.keys())
    query = f"UPDATE system_state SET {set_clause} WHERE id = 1"
    
    # Execute update
    cursor.execute(query, list(state_data.values()))
    
    # Get updated state
    cursor.execute("SELECT * FROM system_state WHERE id = 1")
    row = cursor.fetchone()
    
    conn.commit()
    conn.close()
    
    return _row_to_system_state(row)

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

def _row_to_system_state(row: tuple) -> SystemState:
    """Convert a database row to a SystemState object."""
    return SystemState(
        id=row[0],
        status=SystemStatus(row[1]),
        last_updated=datetime.fromisoformat(row[2]),
        components=json.loads(row[3]) if row[3] else {},
        metrics=json.loads(row[4]) if row[4] else {},
        errors=json.loads(row[5]) if row[5] else [],
        warnings=json.loads(row[6]) if row[6] else [],
        metadata=json.loads(row[7]) if row[7] else {},
        version=row[8],
        uptime=row[9],
        last_backup=datetime.fromisoformat(row[10]) if row[10] else None,
        last_sync=datetime.fromisoformat(row[11]) if row[11] else None,
        active_tasks=row[12],
        pending_tasks=row[13],
        failed_tasks=row[14],
        completed_tasks=row[15],
        resource_usage=json.loads(row[16]) if row[16] else {},
        performance_metrics=json.loads(row[17]) if row[17] else {},
        security_status=json.loads(row[18]) if row[18] else {},
        last_health_check=datetime.fromisoformat(row[19]) if row[19] else None,
        last_maintenance=datetime.fromisoformat(row[20]) if row[20] else None,
        maintenance_mode=bool(row[21]),
        emergency_mode=bool(row[22]),
        last_error=row[23],
        error_count=row[24],
        warning_count=row[25],
        last_alert=datetime.fromisoformat(row[26]) if row[26] else None,
        alert_count=row[27],
        system_load=row[28],
        memory_usage=row[29],
        cpu_usage=row[30],
        disk_usage=row[31],
        network_status=json.loads(row[32]) if row[32] else {},
        last_network_check=datetime.fromisoformat(row[33]) if row[33] else None,
        active_connections=row[34],
        pending_connections=row[35],
        failed_connections=row[36],
        last_connection_error=row[37],
        connection_error_count=row[38],
        last_successful_operation=datetime.fromisoformat(row[39]) if row[39] else None,
        operation_success_rate=row[40],
        last_failed_operation=datetime.fromisoformat(row[41]) if row[41] else None,
        operation_failure_rate=row[42],
        last_recovery=datetime.fromisoformat(row[43]) if row[43] else None,
        recovery_count=row[44],
        last_optimization=datetime.fromisoformat(row[45]) if row[45] else None,
        optimization_status=json.loads(row[46]) if row[46] else {},
        last_cleanup=datetime.fromisoformat(row[47]) if row[47] else None,
        cleanup_status=json.loads(row[48]) if row[48] else {},
        last_update=datetime.fromisoformat(row[49]) if row[49] else None,
        update_status=json.loads(row[50]) if row[50] else {},
        last_backup_size=row[51],
        backup_status=json.loads(row[52]) if row[52] else {},
        last_sync_size=row[53],
        sync_status=json.loads(row[54]) if row[54] else {},
        last_validation=datetime.fromisoformat(row[55]) if row[55] else None,
        validation_status=json.loads(row[56]) if row[56] else {},
        last_integrity_check=datetime.fromisoformat(row[57]) if row[57] else None,
        integrity_status=json.loads(row[58]) if row[58] else {},
        last_security_scan=datetime.fromisoformat(row[59]) if row[59] else None,
        security_scan_status=json.loads(row[60]) if row[60] else {},
        last_performance_test=datetime.fromisoformat(row[61]) if row[61] else None,
        performance_test_status=json.loads(row[62]) if row[62] else {},
        last_load_test=datetime.fromisoformat(row[63]) if row[63] else None,
        load_test_status=json.loads(row[64]) if row[64] else {},
        last_stress_test=datetime.fromisoformat(row[65]) if row[65] else None,
        stress_test_status=json.loads(row[66]) if row[66] else {},
        last_reliability_test=datetime.fromisoformat(row[67]) if row[67] else None,
        reliability_test_status=json.loads(row[68]) if row[68] else {},
        last_compatibility_test=datetime.fromisoformat(row[69]) if row[69] else None,
        compatibility_test_status=json.loads(row[70]) if row[70] else {},
        last_regression_test=datetime.fromisoformat(row[71]) if row[71] else None,
        regression_test_status=json.loads(row[72]) if row[72] else {},
        last_unit_test=datetime.fromisoformat(row[73]) if row[73] else None,
        unit_test_status=json.loads(row[74]) if row[74] else {},
        last_integration_test=datetime.fromisoformat(row[75]) if row[75] else None,
        integration_test_status=json.loads(row[76]) if row[76] else {},
        last_system_test=datetime.fromisoformat(row[77]) if row[77] else None,
        system_test_status=json.loads(row[78]) if row[78] else {},
        last_acceptance_test=datetime.fromisoformat(row[79]) if row[79] else None,
        acceptance_test_status=json.loads(row[80]) if row[80] else {},
        last_user_test=datetime.fromisoformat(row[81]) if row[81] else None,
        user_test_status=json.loads(row[82]) if row[82] else {},
        last_alpha_test=datetime.fromisoformat(row[83]) if row[83] else None,
        alpha_test_status=json.loads(row[84]) if row[84] else {},
        last_beta_test=datetime.fromisoformat(row[85]) if row[85] else None,
        beta_test_status=json.loads(row[86]) if row[86] else {},
        last_gamma_test=datetime.fromisoformat(row[87]) if row[87] else None,
        gamma_test_status=json.loads(row[88]) if row[88] else {},
        last_delta_test=datetime.fromisoformat(row[89]) if row[89] else None,
        delta_test_status=json.loads(row[90]) if row[90] else {},
        last_epsilon_test=datetime.fromisoformat(row[91]) if row[91] else None,
        epsilon_test_status=json.loads(row[92]) if row[92] else {},
        last_zeta_test=datetime.fromisoformat(row[93]) if row[93] else None,
        zeta_test_status=json.loads(row[94]) if row[94] else {},
        last_eta_test=datetime.fromisoformat(row[95]) if row[95] else None,
        eta_test_status=json.loads(row[96]) if row[96] else {},
        last_theta_test=datetime.fromisoformat(row[97]) if row[97] else None,
        theta_test_status=json.loads(row[98]) if row[98] else {},
        last_iota_test=datetime.fromisoformat(row[99]) if row[99] else None,
        iota_test_status=json.loads(row[100]) if row[100] else {},
        last_kappa_test=datetime.fromisoformat(row[101]) if row[101] else None,
        kappa_test_status=json.loads(row[102]) if row[102] else {},
        last_lambda_test=datetime.fromisoformat(row[103]) if row[103] else None,
        lambda_test_status=json.loads(row[104]) if row[104] else {},
        last_mu_test=datetime.fromisoformat(row[105]) if row[105] else None,
        mu_test_status=json.loads(row[106]) if row[106] else {},
        last_nu_test=datetime.fromisoformat(row[107]) if row[107] else None,
        nu_test_status=json.loads(row[108]) if row[108] else {},
        last_xi_test=datetime.fromisoformat(row[109]) if row[109] else None,
        xi_test_status=json.loads(row[110]) if row[110] else {},
        last_omicron_test=datetime.fromisoformat(row[111]) if row[111] else None,
        omicron_test_status=json.loads(row[112]) if row[112] else {},
        last_pi_test=datetime.fromisoformat(row[113]) if row[113] else None,
        pi_test_status=json.loads(row[114]) if row[114] else {},
        last_rho_test=datetime.fromisoformat(row[115]) if row[115] else None,
        rho_test_status=json.loads(row[116]) if row[116] else {},
        last_sigma_test=datetime.fromisoformat(row[117]) if row[117] else None,
        sigma_test_status=json.loads(row[118]) if row[118] else {},
        last_tau_test=datetime.fromisoformat(row[119]) if row[119] else None,
        tau_test_status=json.loads(row[120]) if row[120] else {},
        last_upsilon_test=datetime.fromisoformat(row[121]) if row[121] else None,
        upsilon_test_status=json.loads(row[122]) if row[122] else {},
        last_phi_test=datetime.fromisoformat(row[123]) if row[123] else None,
        phi_test_status=json.loads(row[124]) if row[124] else {},
        last_chi_test=datetime.fromisoformat(row[125]) if row[125] else None,
        chi_test_status=json.loads(row[126]) if row[126] else {},
        last_psi_test=datetime.fromisoformat(row[127]) if row[127] else None,
        psi_test_status=json.loads(row[128]) if row[128] else {},
        last_omega_test=datetime.fromisoformat(row[129]) if row[129] else None,
        omega_test_status=json.loads(row[130]) if row[130] else {}
    ) 
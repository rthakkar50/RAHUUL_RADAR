"""
RAHUUL RADAR — Enterprise Operations & SRE Platform: Domain Models
====================================================================
Data contracts and models for SRE health, metrics, alerts, audit, backup, and security.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class SystemHealthStatus:
    overall_status: str  # "HEALTHY", "DEGRADED", "UNHEALTHY"
    api_status: str
    db_status: str
    ai_status: str
    fno_status: str
    paper_status: str
    telegram_status: str
    broker_status: str
    cpu_pct: float
    memory_pct: float
    disk_pct: float
    timestamp: str = ""


@dataclass
class MetricEntry:
    metric_name: str
    value: float
    unit: str
    category: str
    timestamp: str = ""


@dataclass
class AlertItem:
    alert_id: str
    severity: str  # "INFO", "WARNING", "CRITICAL"
    source: str
    title: str
    message: str
    timestamp: str = ""
    resolved: bool = False


@dataclass
class AuditLogEntry:
    audit_id: str
    event_type: str  # "ORDER", "AI_DECISION", "RISK_DECISION", "SYSTEM", "USER"
    source_module: str
    action: str
    details: Dict[str, Any]
    timestamp: str = ""
    sensitive_redacted: bool = True


@dataclass
class BackupResult:
    backup_id: str
    timestamp: str
    files_backed_up: List[str]
    total_size_bytes: int
    checksum: str
    is_verified: bool = True


@dataclass
class RestoreResult:
    restore_id: str
    timestamp: str
    restored_files: List[str]
    is_successful: bool = True
    verification_notes: str = ""


@dataclass
class ConfigValidationReport:
    is_valid: bool
    missing_keys: List[str]
    environment_status: str
    version_metadata: Dict[str, str]

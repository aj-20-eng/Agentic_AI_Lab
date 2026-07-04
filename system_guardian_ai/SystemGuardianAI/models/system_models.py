"""
System Guardian AI

Author : Amit Kr Jha
Description:
Data models used across the entire application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


# ---------------- CPU ---------------- #

@dataclass
class CPUInfo:
    usage: float
    physical_cores: int
    logical_cores: int
    current_frequency: float
    max_frequency: float
    per_core_usage: List[float]


# ---------------- Memory ---------------- #

@dataclass
class MemoryInfo:
    total_gb: float
    used_gb: float
    available_gb: float
    percent: float


# ---------------- Disk ---------------- #

@dataclass
class DiskInfo:
    drive: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent: float
    file_system: str


# ---------------- Process ---------------- #

@dataclass
class ProcessInfo:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str


# ---------------- Health ---------------- #

@dataclass
class HealthStatus:
    cpu_status: str
    ram_status: str
    disk_status: str
    score: int


# ---------------- Snapshot ---------------- #

@dataclass
class SystemSnapshot:

    timestamp: datetime

    cpu: CPUInfo

    memory: MemoryInfo

    disks: List[DiskInfo]

    processes: List[ProcessInfo]

    health: HealthStatus
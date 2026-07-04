"""
Memory Collector
"""

import psutil

from models.system_models import MemoryInfo


class MemoryCollector:

    def collect(self) -> MemoryInfo:

        mem = psutil.virtual_memory()

        return MemoryInfo(
            total_gb=round(mem.total / (1024 ** 3), 2),
            used_gb=round(mem.used / (1024 ** 3), 2),
            available_gb=round(mem.available / (1024 ** 3), 2),
            percent=mem.percent,
        )
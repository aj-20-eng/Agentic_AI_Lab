"""
CPU Collector
"""

import psutil

from models.system_models import CPUInfo


class CPUCollector:

    def collect(self) -> CPUInfo:

        freq = psutil.cpu_freq()

        return CPUInfo(
            usage=psutil.cpu_percent(interval=1),
            physical_cores=psutil.cpu_count(logical=False),
            logical_cores=psutil.cpu_count(logical=True),
            current_frequency=round(freq.current, 2),
            max_frequency=round(freq.max, 2),
            per_core_usage=psutil.cpu_percent(interval=None, percpu=True),
        )
"""
Health Service
"""

from models.system_models import HealthStatus


class HealthService:

    def evaluate(self, cpu, memory, disks):

        cpu_state = "Healthy"
        ram_state = "Healthy"
        disk_state = "Healthy"

        score = 100

        if cpu.usage > 70:
            cpu_state = "Warning"
            score -= 10

        if cpu.usage > 90:
            cpu_state = "Critical"
            score -= 10

        if memory.percent > 80:
            ram_state = "Warning"
            score -= 10

        if memory.percent > 90:
            ram_state = "Critical"
            score -= 10

        for disk in disks:

            if disk.percent > 80:
                disk_state = "Warning"
                score -= 15

            if disk.percent > 90:
                disk_state = "Critical"
                score -= 15

        return HealthStatus(
            cpu_status=cpu_state,
            ram_status=ram_state,
            disk_status=disk_state,
            score=max(score, 0),
        )
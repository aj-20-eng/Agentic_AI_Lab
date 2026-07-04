"""
Foundation Test
"""

from collectors.cpu_collector import CPUCollector
from collectors.memory_collector import MemoryCollector

from services.health_service import HealthService


def main():

    print("=" * 60)
    print("SYSTEM GUARDIAN AI - FOUNDATION TEST")
    print("=" * 60)

    cpu = CPUCollector().collect()
    memory = MemoryCollector().collect()

    # Temporary empty disk list
    disks = []

    health = HealthService().evaluate(cpu, memory, disks)

    print("\nCPU INFORMATION")
    print("-" * 60)
    print(f"Usage             : {cpu.usage}%")
    print(f"Physical Cores    : {cpu.physical_cores}")
    print(f"Logical Cores     : {cpu.logical_cores}")
    print(f"Current Frequency : {cpu.current_frequency} MHz")
    print(f"Max Frequency     : {cpu.max_frequency} MHz")
    print(f"Per Core Usage    : {cpu.per_core_usage}")

    print("\nMEMORY INFORMATION")
    print("-" * 60)
    print(f"Total RAM         : {memory.total_gb} GB")
    print(f"Used RAM          : {memory.used_gb} GB")
    print(f"Available RAM     : {memory.available_gb} GB")
    print(f"Usage             : {memory.percent}%")

    print("\nHEALTH STATUS")
    print("-" * 60)
    print(f"CPU Status        : {health.cpu_status}")
    print(f"RAM Status        : {health.ram_status}")
    print(f"Disk Status       : {health.disk_status}")
    print(f"Health Score      : {health.score}/100")


if __name__ == "__main__":
    main()
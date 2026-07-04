"""
============================================================
System Guardian AI
Version : 0.1 (Foundation)
Author  : Amit Kr Jha

Entry point of the application.
============================================================
"""

import os
import time
from datetime import datetime

from collectors.cpu_collector import CPUCollector
from collectors.memory_collector import MemoryCollector
from services.health_service import HealthService


class SystemGuardian:
    """
    Main Application Class
    """

    def __init__(self):

        self.cpu_collector = CPUCollector()
        self.memory_collector = MemoryCollector()
        self.health_service = HealthService()

    # -------------------------------------------------------
    # Clear Console
    # -------------------------------------------------------
    def clear_screen(self):

        os.system("cls" if os.name == "nt" else "clear")

    # -------------------------------------------------------
    # Header
    # -------------------------------------------------------
    def display_header(self):

        print("=" * 70)
        print("               SYSTEM GUARDIAN AI")
        print("                  Version 0.1")
        print("=" * 70)

        print(f"Time : {datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')}")
        print()

    # -------------------------------------------------------
    # CPU
    # -------------------------------------------------------
    def display_cpu(self, cpu):

        print("CPU INFORMATION")
        print("-" * 70)

        print(f"CPU Usage          : {cpu.usage}%")
        print(f"Physical Cores     : {cpu.physical_cores}")
        print(f"Logical Cores      : {cpu.logical_cores}")
        print(f"Current Frequency  : {cpu.current_frequency} MHz")
        print(f"Maximum Frequency  : {cpu.max_frequency} MHz")

        print()
        print("Per Core Usage")
        print("-" * 70)

        for index, usage in enumerate(cpu.per_core_usage, start=1):

            print(f"Core {index:02d} : {usage}%")

    # -------------------------------------------------------
    # Memory
    # -------------------------------------------------------
    def display_memory(self, memory):

        print()
        print("MEMORY INFORMATION")
        print("-" * 70)

        print(f"Total RAM      : {memory.total_gb} GB")
        print(f"Used RAM       : {memory.used_gb} GB")
        print(f"Available RAM  : {memory.available_gb} GB")
        print(f"RAM Usage      : {memory.percent}%")

    # -------------------------------------------------------
    # Health
    # -------------------------------------------------------
    def display_health(self, health):

        print()
        print("SYSTEM HEALTH")
        print("-" * 70)

        print(f"CPU Status     : {health.cpu_status}")
        print(f"RAM Status     : {health.ram_status}")
        print(f"Disk Status    : {health.disk_status}")
        print(f"Health Score   : {health.score}/100")

    # -------------------------------------------------------
    # Run Application
    # -------------------------------------------------------
    def run(self):

        try:

            while True:

                self.clear_screen()

                cpu = self.cpu_collector.collect()
                memory = self.memory_collector.collect()

                health = self.health_service.evaluate(
                    cpu,
                    memory,
                    []
                )

                self.display_header()
                self.display_cpu(cpu)
                self.display_memory(memory)
                self.display_health(health)

                print()
                print("=" * 70)
                print("Refreshing every 10 seconds...")
                print("Press CTRL + C to stop")
                print("=" * 70)

                time.sleep(10)

        except KeyboardInterrupt:

            print("\n")
            print("=" * 70)
            print("System Guardian AI stopped.")
            print("=" * 70)


# ===========================================================
# Main
# ===========================================================

if __name__ == "__main__":

    app = SystemGuardian()

    app.run()
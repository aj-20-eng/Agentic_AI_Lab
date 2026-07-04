import psutil


def get_top_processes(limit=10):

    processes = []

    for process in psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_percent"]
    ):

        try:

            processes.append(
                {
                    "pid": process.info["pid"],
                    "name": process.info["name"],
                    "cpu": process.info["cpu_percent"],
                    "memory": round(process.info["memory_percent"], 2),
                }
            )

        except Exception:
            pass

    processes = sorted(
        processes,
        key=lambda x: (x["cpu"], x["memory"]),
        reverse=True,
    )

    return processes[:limit]
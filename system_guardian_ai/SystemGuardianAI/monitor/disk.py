import psutil


def get_disk_usage():

    disk = psutil.disk_usage("C:\\")

    return {
        "total": round(disk.total / (1024 ** 3), 2),
        "used": round(disk.used / (1024 ** 3), 2),
        "free": round(disk.free / (1024 ** 3), 2),
        "percent": disk.percent,
    }
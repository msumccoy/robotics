import subprocess

from variables import Alert


class Conf:
    RAM_DISK_NAME = "system_ramdisk"
    sub_proc = subprocess.run(["cat", "/proc/mounts"], stdout=subprocess.PIPE)
    if RAM_DISK_NAME not in sub_proc.stdout.decode("utf-8"):
        Alert.ramdisk = True

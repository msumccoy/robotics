import json
import os
import subprocess

from variables import Alert

config_file = "/home/pi/file.json"  # This is system specific
config_file = "/home/kuwin/file2.json"  # This is system specific
with open(config_file) as file:
    config = json.load(file)


class Conf:
    PATH_ROOT = config["path"]  # Typically: /home/pi/Documents/Code/
    PATH_ROOT += "test_files/"  # only for test environment
    RAM_DISK = "system_ramdisk"
    PIPE_PATH = f"{PATH_ROOT}{RAM_DISK}/pipes/"
    PIPE_GUI = f"{PIPE_PATH}gui"  # FIFO for gui
    sub_proc = subprocess.run(["cat", "/proc/mounts"], stdout=subprocess.PIPE)
    if RAM_DISK in sub_proc.stdout.decode("utf-8"):
        Alert.ramdisk = True
        if not os.path.exists(PIPE_PATH):
            os.mkdir(PIPE_PATH)

        if not os.path.exists(PIPE_GUI):
            os.mkfifo(PIPE_GUI)


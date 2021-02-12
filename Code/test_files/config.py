import json
import os
import subprocess

from variables import Active

config_file = "/home/pi/file.json"  # This is system specific
config_file = "/home/kuwin/file2.json"  # This is system specific
with open(config_file) as file:
    config = json.load(file)


class Conf:
    PATH_ROOT = config["path"]  # Typically: /home/pi/Documents/Code/
    PATH_ROOT += "test_files/"  # only for test environment
    PIPE_PATH = f"{PATH_ROOT}/pipes/"
    PIPE_GUI = f"{PIPE_PATH}gui"  # FIFO for gui
    RAM_DISK = "system_ramdisk"
    if not os.path.exists(PIPE_GUI):
        os.mkfifo(PIPE_GUI)

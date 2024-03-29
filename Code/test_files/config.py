import json
import os
import subprocess


config_file = "/home/pi/file.json"  # This is system specific
config_file = "/home/kuwin/file2.json"  # This is system specific
with open(config_file) as file:
    config = json.load(file)


class Conf:
    PATH_ROOT = config["path"]  # Typically: /home/pi/Documents/Code/
    PATH_ROOT += "test_files/"  # only for test environment

    # Socket server settings  ################################################
    LOCAL_IP = "127.0.0.1"
    PING_MONITOR_IP = "127.0.0.1"
    PING_MONITOR_PORT = 1234
    PRE_HEADER_LEN = 3
    HEADER_LEN = 10
    ENCODING = "utf-8"

    COM_IMG = 10
    COM_IMG_REQUEST = 11
    COM_TEST = 100
    COM_TEST2 = 12
    # Communication constants Constants  #####################################
    COM_TEST = 0
    NUM_SEGMENTS = 0

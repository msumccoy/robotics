""" Kuwin Wyke
Midwestern State University

This module contains the class that is ued to handle all logging operations
"""
import threading
import os

from config import LogConf


class LogMaster:
    _inst = None
    _lock = threading.Lock()

    @staticmethod
    def get_inst():
        # Function to allow all functions to use one instance of the class.
        with LogMaster._lock:
            # If a lock is not used then functions acquire different instances
            # of the class
            if LogMaster._inst is None:
                LogMaster._inst = LogMaster()
            return LogMaster._inst

    def __init__(self, log_path=LogConf.PATH, log_file=LogConf.FILE):
        self.path = log_path
        self.file = log_file
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def log(self, message):
        with self._lock:
            with open(self.path + self.file, "a") as file:
                file.write(message)
        print(message)

"""
Kuwin Wyke
Midwestern State University


This module is used to control how often the timing of execution is writen to
file
"""
import time

from ball_recognition_haar.config import Log


class LogFrequency:
    _inst_dict = {}

    def __init__(self):
        self.start = 0

    @staticmethod
    def get_inst(name):
        if name not in LogFrequency._inst_dict:
            LogFrequency._inst_dict[name] = LogFrequency()
        return LogFrequency._inst_dict[name]

    def check_interval(self):
        if Log.WRITE_FREQUENCY < time.time() - self.start:
            self.start = time.time()
            return True
        else:
            return False

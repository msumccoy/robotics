"""Kuwin Wyke
Midwestern State University
Start: 6 November 2019
End: work in progress

This module is designed to be used in the ball recognition program in the
folder named "ball_recognition_v1". This module contains the variables to
control debug settings. It also contains functions to perform debugging tasks.

Classes:


Functions:
"""

import time

debug_gen = 0
debug_cam = 0
debug_circles = 0
debug_cycles = 0
debug_robot = 0

debug_all = 0
if debug_all:
    debug_cam = 1
    debug_circles = 1
    debug_cycles = 1
    debug_robot = 1

output_frequency = 5

class ExecutionTiming:
    # This class is used to check the duration something start to execute
    # It also calculates average execution time
    cycles = 0
    last_output = 0

    def __init__(self):
        self.start()

    def start(self):
        self.start_time = time.time()

    def check(self):
        self.cycles += 1
        total_time = time.time() - self.start_time
        average = total_time / self.cycles
        if time.time() - self.last_output > output_frequency and debug_cycles:
            print("Total time = ", total_time)
            print("Average execution time = ", average)
            self.last_output = time.time()


class ErrorOutput:
    last_output = 0
    def __init__(self):
        pass

    def error_output(self, error):
        if (time.time() - self.last_output > output_frequency
                and debug_circles) :
            print(error)
            self.last_output = time.time()

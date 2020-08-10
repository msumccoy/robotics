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


class Debug:
    output_frequency = 5

    gen = 0
    cam = 0
    circles = 0
    cycles = 0
    robot = 0

    debug_all = 0
    if debug_all:
        gen = 1
        cam = 1
        circles = 1
        cycles = 1
        robot = 1

    @staticmethod
    def debug_on():
        Debug.cam = 1
        Debug.circles = 1
        Debug.cycles = 1
        Debug.robot = 1
        print("debug on")

    @staticmethod
    def debug_off():
        Debug.cam = 0
        Debug.circles = 0
        Debug.cycles = 0
        Debug.robot = 0
        print("debug off")


class ExecutionTiming:
    # This class is used to check the duration something start to execute
    # It also calculates average execution time
    cycles = 0
    last_output = 0

    def __init__(self,):
        self.start_time = time.time()
        self.cycles = 0
        self.last_output = 0

    def check(self):
        self.cycles += 1
        if Debug.cycles:
            total_time = time.time() - self.start_time
            average = total_time / self.cycles
            if time.time() - self.last_output > Debug.output_frequency:
                print("Total time = ", total_time)
                print("Average execution time = ", average)
                self.last_output = time.time()


class ErrorOutput:
    def __init__(self):
        self.last_output = 0

    def error_output(self, error):
        if Debug.circles:
            if time.time() - self.last_output > Debug.output_frequency:
                print(error)
                self.last_output = time.time()

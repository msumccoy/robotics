""" Kuwin Wyke
Midwestern State University
Start: 1 November 2019
End: Work in progress

This module is designed to be used in the ball recognition program in the
folder named "ball_recognition_v1". It possess most of the variables to be
used within the program including dictionaries with all valid motions in
heart2heart.

ALL debug related variables and functions can be found in debug.py
"""

# Used for testing purposes. This activates the test environment in the event
# the robot is not available or there is risky code to be tested
import numpy as np


class RobotCom:
    # Used to activate and deactivate automatic movement of the robot
    automatic_control = 1


# Filter specific variables **************************************************
class FilterVariables:
    _inst = None

    @staticmethod
    def get_inst():
        if FilterVariables._inst is None:
            FilterVariables._inst = FilterVariables()
        return FilterVariables._inst

    def __init__(self):
        # Set path to variables file
        self._file = "filter_variables.txt"
        # Read variables from file
        with open(self._file, "r") as file:
            self.lower_limit = int(file.readline())
            self.lower_limit2 = int(file.readline())
            self.lower_limit_hue = int(file.readline())
            self.upper_limit = int(file.readline())
            self.upper_limit2 = int(file.readline())
            self.upper_limit_hue = int(file.readline())
            self.circle_detect_param = int(file.readline())
            self.circle_detect_param2 = int(file.readline())

        # Create arrays for filter parameters
        self.lower_range = np.array(
            [
                self.lower_limit_hue,
                self.lower_limit,
                self.lower_limit2
            ]
        )
        self.upper_range = np.array(
            [
                self.upper_limit_hue,
                self.upper_limit,
                self.upper_limit2
            ]
        )

    def file_save(self):
        print("saving filter variables file")
        string = str(self.lower_limit) + '\n'
        string += str(self.lower_limit2) + '\n'
        string += str(self.lower_limit_hue) + '\n'
        string += str(self.upper_limit) + '\n'
        string += str(self.upper_limit2) + '\n'
        string += str(self.upper_limit_hue) + '\n'
        string += str(self.circle_detect_param) + '\n'
        string += str(self.circle_detect_param2)
        with open(self._file, "w") as file:
            file.write(string)

    def get_ranges(self):
        ary = [
            self.lower_range,
            self.upper_range
        ]
        return ary

    def get_circle_params(self):
        ary = [
            self.circle_detect_param,
            self.circle_detect_param2
        ]
        return ary

    def get_lower(self):
        ary = [
            self.lower_limit,
            self.lower_limit2,
            self.lower_limit_hue,
        ]
        return ary

    def get_upper(self):
        ary = [
            self.upper_limit,
            self.upper_limit2,
            self.upper_limit_hue,
        ]
        return ary

    def update_ranges(self):
        # Create arrays for filter parameters
        self.lower_range = np.array(
            [
                self.lower_limit_hue,
                self.lower_limit,
                self.lower_limit2
            ]
        )
        self.upper_range = np.array(
            [
                self.upper_limit_hue,
                self.upper_limit,
                self.upper_limit2
            ]
        )

    def update_lower_limit(self, value):
        self.lower_limit = value

    def update_lower_limit2(self, value):
        self.lower_limit2 = value

    def update_lower_limit_hue(self, value):
        self.lower_limit_hue = value

    def update_upper_limit(self, value):
        self.upper_limit = value

    def update_upper_limit2(self, value):
        self.upper_limit2 = value

    def update_upper_limit_hue(self, value):
        self.upper_limit_hue = value

    def update_circle_detect_param(self, value):
        self.circle_detect_param = value

    def update_circle_detect_param2(self, value):
        self.circle_detect_param2 = value


class ExitControl:
    # General exit flag
    gen = 0
    remote = 0
    # Exit flag for ball detection
    detection = 0
    # Exit flag for calibration loop
    calibrate = 0

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
test_environment = True

import numpy as np
from threading import Lock

# Motion number dictionaries**************************************************
full_motion_dictionary = {  # Full dictionary with all motions in Heart2Heart
    0: "Bow -- not working",
    1: "Home position",
    2: "Waving",
    3: "stretch",
    4: "Craw like motion",
    5: "Dance (hard on servos)",
    6: "Don't know",
    7: "Clap 1",
    8: "Clap 2",
    9: "Push ups",
    10: "Don't know (hard on servos)",
    11: "Jump 3 times (worst on servo)",
    12: "Get off the ground (direction sensing)",
    13: "Get off the ground (face down)",
    14: "Get off the ground (face up)",
    15: "Move forward 5 steps (slowly)",
    16: "Move backward 5 steps (slowly)",
    17: "Move left 5 steps (slowly)",
    18: "Move right 5 steps (slowly)",
    19: "Turn left (5 step turn)",
    20: "Turn right (5 step turn)",
    21: "Move forward 5 steps (fast but more unstable)",
    22: "Move backward 5 steps (fast but more unstable)",
    23: "Move left 5 steps (fast but more unstable)",
    24: "Move right 5 steps (fast but more unstable)",
    25: "Kick forward with left foot",
    26: "Kick forward with right foot",
    27: "*not sure* kick with left foot",
    28: "*not sure* kick with right foot",
    29: "Kick back with left foot",
    30: "Kick back with right foot",
    31: "Empty",
    32: "Defense (fighting)",
    33: "Punch forward (fighting)",
    34: "Left punch (fighting)",
    35: "Right punch (fighting)",
    36: "pose",
    37: "pose",
    38: "Empty",
    39: "cannot use",
    40: "cannot use",
    41: "cannot use",
    42: "cannot use",
    43: "cannot use",
    44: "cannot use",
    45: "cannot use",
    46: "cannot use",
    47: "cannot use",
    48: "cannot use",
    49: "cannot use",
    50: "cannot use",
}

motion_dictionary = {  # Condensed dictionary for all accepted movements
    1: "Home position",
    2: "Waving",
    3: "stretch",
    4: "Craw like motion",
    7: "Clap 1",
    8: "Clap 2",
    9: "Push ups",
    12: "Get off the ground (direction sensing)",
    13: "Get off the ground (face down)",
    14: "Get off the ground (face up)",
    15: "Move forward 5 steps (slowly)",
    16: "Move backward 5 steps (slowly)",
    17: "Move left 5 steps (slowly)",
    18: "Move right 5 steps (slowly)",
    19: "Turn left (5 step turn)",
    20: "Turn right (5 step turn)",
    21: "Move forward 5 steps (fast but more unstable)",
    22: "Move backward 5 steps (fast but more unstable)",
    23: "Move left 5 steps (fast but more unstable)",
    24: "Move right 5 steps (fast but more unstable)",
    25: "Kick forward with left foot",
    26: "Kick forward with right foot",
    27: "*not sure* kick with left foot",
    28: "*not sure* kick with right foot",
    29: "Kick back with left foot",
    30: "Kick back with right foot",
    36: "pose",
    37: "pose",
}

# Robot motion specific variables*********************************************
ok_response = r"\x04\xfe\x06\x08"
stop_motion = r"\x09\x00\x02\x00\x00\x00\x10\x83\x9e"
reset_counter = (
    r"\x11\x00\x02\x02\x00\x00\x4b\x04\x00\x00\x00\x00\x00\x00\x00\x00\x64")

# Robot control variables*****************************************************

# Create variable for the communication port name
com_port = "/dev/rfcomm2"
# Set time wait time for port communication (initial) must be long enough to
# accommodate robot action
connection_time_out = 5
# Set wait time for blue tooth connection
serial_port_time_out = 5

# Camera specific variables **************************************************

# Set a default height and width (if the dimensions are off (incorrect) they
# may change.
set_width = 320
set_height = 240

# Filter specific variables **************************************************

# Set path to variables file
variables_file = "filter_variables.txt"
# Read variables from file
variables = open(variables_file, "r")
lower_limit = int(variables.readline())
lower_limit2 = int(variables.readline())
lower_limit_hue = int(variables.readline())
upper_limit = int(variables.readline())
upper_limit2 = int(variables.readline())
upper_limit_hue = int(variables.readline())
circle_detect_param = int(variables.readline())
circle_detect_param2 = int(variables.readline())
variables.close()

# Create arrays for filter parameters
lower_range = np.array([lower_limit_hue, lower_limit, lower_limit2])
upper_range = np.array([upper_limit_hue, upper_limit, upper_limit2])

# Create threading specific variables  ***************************************
lock = Lock()
thread_motion_num = -1
# General exit flag
exit_gen = 0
# Exit flag for ball detection
exit_detect = 0
# Exit flag for calibration loop
exit_calibrate = 0
# Used to activate and deactivate automatic movement of the robot
automatic_control = 1

if __name__ == "__main__":
    for i in motion_dictionary:
        print(i, " : ", motion_dictionary[i])

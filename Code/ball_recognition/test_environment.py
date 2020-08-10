""" Kuwin Wyke
Midwestern State University
Start: 6 November 2019
End: work in progress

This module is designed to be used in the ball recognition program in the
folder named "ball_recognition_v1". It contains classes and functions to be
used when not executing the main function on a raspberry pi connected to
the robot.
"""

import time

# Project specific modules
import variables
import control_functions


# Dummy code to handle lack of serial class on windows pc
def decode(hex_string):
    """
    This function decodes hex strings. Currently only decodes motion strings
    to in a minimal degree.
    :param hex_string: this is a hex string that would be sent to the robot
    :return:
    """

    alert_window = control_functions.AlertWindow("Robot action")
    pause = 0.3
    pause_multiplier = 10
    hex_string_array = hex_string[2:].split(r"\x")
    sum = 0
    for index in range(len(hex_string_array)):
        if index != len(hex_string_array) - 1:
            try:
                sum += int(hex_string_array[index], 16)
            except:
                print("Hex to decimal fail")
    # Convert sum to hex and truncate to only the last two digits
    sum = hex(sum)[-2:]
    if sum == hex_string_array[-1]:
        print("Check sum good")
    if len(hex_string_array) == int(hex_string_array[0], 16):
        print("Length good")
        motion = (int(hex_string_array[4] + hex_string_array[3], 16))
        motion = (motion - 11)
        motion = motion/ 8
        for cycle in range(pause_multiplier, 0, -1):
            message = (variables.full_motion_dictionary[motion])
            message += " " + str(cycle)
            alert_window.output_window(message)
            time.sleep(pause)
    print("motion complete: ",
          variables.full_motion_dictionary[motion])
    return variables.ok_response


class serial:
    """
    This is a dummy used as a place holder in lieu of the actual serial
    module on the raspberry pi.
    """
    # Place holders
    EIGHTBITS = None
    PARITY_EVEN = None
    STOPBITS_ONE = None

    class Serial:
        def __init__(self, *args, **kwargs):
            # This is just so that there is a place for the arguments that
            # would normally be passed.
            pass

        count = 0
        count2 = 0

        def Open(self):
            pass

        def isOpen(self):
            self.count += 1
            if self.count > 1000:
                return variables.ok_response

        def close(self):
            # print("serial close")
            pass

        def read(self):
            # print("serial read")
            # self.count2 += 1
            return variables.ok_response

        def write(self, hex_string=""):
            # print("serial write : ", hex_string)
            decode(hex_string)

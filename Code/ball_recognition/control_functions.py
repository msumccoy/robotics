""" Kuwin Wyke
Midwestern State University
Start: 11 November 2019
End: work in progress

This module is designed to be used in the ball recognition program in the
folder named "ball_recognition_v1". It contains functions to be used within
the main function loop as options.
"""

import cv2
import numpy as np

# Project specific modules
import variables


# This class is used to create opencv alert windows to display information
# without having to print to the console
class AlertWindow:
    font = cv2.FONT_HERSHEY_PLAIN
    font_scale = 2
    text_color = (255, 255, 255)
    thickness = 2
    line = cv2.LINE_AA

    def __init__(self, window):
        self.window = window

    def output_window(self, message):
        background = np.zeros((128, 512, 3), np.uint8)
        background = cv2.putText(background, message, (10, 50), self.font,
                                 self.font_scale, self.text_color,
                                 self.thickness, self.line)
        cv2.imshow(self.window, background)
        cv2.waitKey(1)

    def __del__(self):
        cv2.destroyWindow(self.window)


# This function is used to send motion commands to the robot
def send_command(robot, motion_num, dictionary=variables.motion_dictionary):
    try:
        motion_num = int(motion_num)
        if motion_num in dictionary:
            robot.send_motion_cmd(motion_num)
        elif motion_num < 0:
            with variables.lock:
                variables.exit_gen = 1
            print("exiting")
        else:
            print("Invalid option")
    except Exception as e:
        print("Error in motion conversion\n error is ", e)


# This function is used to stop the current robot motion and disable automatic
# control of the robot.
def stop_motion(robot):
    print("Stop robot")
    motion_num = "stop"
    with variables.lock:
        # Disable automatic control
        variables.automatic_control = 0
    print("detect off")
    robot.send_motion_cmd(motion_num)


# Enable detection motion control
def detect_on():
    with variables.lock:
        variables.automatic_control = 1
    print("detect start")


# Disable detection motion control
def detect_off():
    with variables.lock:
        variables.automatic_control = 0
    print("detect stop")


# Set exit flag
def exit_program():
    with variables.lock:
        variables.exit_gen = 1
    print("exiting")

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
from variables import ExitControl, RobotCom
from constants import CV2Window, Locks


# This class is used to create opencv alert windows to display information
# without having to print to the console
class AlertWindow:
    def __init__(self, window_name):
        self.window = window_name

    def output(self, message):
        background = np.zeros(CV2Window.SIZE, np.uint8)
        background = cv2.putText(
            background, message, (10, 50), CV2Window.FONT,
            CV2Window.FONT_SCALE, CV2Window.TEXT_COLOR,
            CV2Window.THICKNESS, CV2Window.LINE)
        cv2.imshow(self.window, background)
        cv2.waitKey(1)

    def __del__(self):
        cv2.destroyWindow(self.window)


class Funcs:
    # This function is used to send motion commands to the robot
    @staticmethod
    def send_command(robot, motion_num, dictionary):
        try:
            motion_num = int(motion_num)
            if motion_num in dictionary:
                robot.send_motion_cmd(motion_num)
            else:
                print("Invalid option")
        except Exception as e:
            print("Error in motion conversion\n error is ", e)

    # This function is used to stop the current robot motion and disable
    # automatic control of the robot.
    @staticmethod
    def stop_motion(robot):
        print("Stop robot")
        motion_num = "stop"
        with Locks.GEN_LOCK:
            # Disable automatic control
            RobotCom.automatic_control = 0
        print("detect off")
        robot.send_motion_cmd(motion_num)

    # Enable detection motion control
    @staticmethod
    def detect_on():
        with Locks.ROBOT_LOCK:
            RobotCom.automatic_control = 1
        print("detect start")

    # Disable detection motion control
    @staticmethod
    def detect_off():
        with Locks.ROBOT_LOCK:
            RobotCom.automatic_control = 0
        print("detect stop")

    # Set exit flag
    @staticmethod
    def exit_program():
        ExitControl.gen = 1
        print("exiting")

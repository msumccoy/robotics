""" Kuwin Wyke
Midwestern State University
Start: 10 October 2019
End: work in progress

This program detects a ball by using a filter that looks only for the color
of the ball. There is a function to manually calibrate the filter. Once only
the color of the ball is detected as input, the program looks for a circle
using a built in OpenCV function. There is also a function to draw the
detected circle and a box around the circle. The box is drawn to demonstrate
the ability to make a ROI (region of interest) to use later when implementing
Haar cascades.

Programed on windows
tested on windows 10 and raspberry pi (debian jessie).
both: python 3
raspberry pi: opencv version 4.0.0 (does not function correctly on idle)
windows: opencv version 4.1.1
"""

import threading
import cv2

# Project specific modules
import misc
from variables import ExitControl,FilterVariables, RobotCom
from constants import HexConst, Locks, KeyWordControl, R_Control, DICTS
from control_humanoid import control_humanoid
from control_spider import control_spider
from circle_detection import ObjectDetector
from robot_control import Robot
from debug import Debug
from control_functions import Funcs

from picamera.array import PiRGBArray
from picamera import PiCamera


def main():
    # Create objects to control robot and circle detection/calibration
    # control_humanoid()
    control_spider()


if __name__ == "__main__":
    main()

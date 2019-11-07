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

# Project specific modules
import variables
import circle_detection
import robot_control


def main():
    """
    """
    circle_detection.calibrate_filter()
    robot = robot_control.Robot()
    robot_thread = threading.Thread(target=robot_control.robot_control,
                                    args=(robot,))
    manual_robot_thread = threading.Thread(target=robot.manual_control)
    object_detector_thread = (
        threading.Thread(target=circle_detection.object_detection))
    robot_thread.start()
    manual_robot_thread.start()
    object_detector_thread.start()
    manual_robot_thread.join()
    object_detector_thread.join()
    with variables.lock:
        variables.exit_code = 1
    pass


if __name__ == "__main__":
    main()

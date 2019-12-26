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
import const
import circle_detection
import robot_control
import debug


def main():
    object_detector = circle_detection.ObjectDetection()
    object_detector_thread = (
        threading.Thread(target=object_detector.object_detection,))

    robot = robot_control.Robot()
    automatic_robot_thread = threading.Thread(
        target=robot.automatic_control)

    automatic_robot_thread.start()
    object_detector_thread.start()

    try:
        while 1:
            motion_num = input("Enter motion number \n")
            # Give access to full range of motions
            if motion_num == const.FULL_CONTROL:
                print("full control")
                motion_num = input("Enter full motion number \n")
                # Print dictionary
                if motion_num == const.DICTIONARY:
                    for key in variables.full_motion_dictionary:
                        print(key, " : ",
                              variables.full_motion_dictionary[key])
                    motion_num = input("Enter full motion number from dict\n")
                # Make sure an integer was entered
                try:
                    motion_num = int(motion_num)
                except Exception as e:
                    print("Error in motion conversion\n error is ", e)
                    motion_num = "not valid"
                if motion_num == "not valid":
                    print("not valid")
                elif motion_num in variables.full_motion_dictionary:
                    robot.send_motion_cmd(motion_num)
                else:
                    print("Invalid option: full control")

            # Print dictionary
            elif motion_num == const.DICTIONARY:
                for key in variables.motion_dictionary:
                    print(key, " : ", variables.motion_dictionary[key])

            # Stop robot current motion
            elif motion_num == "stop" or motion_num == "s":
                print("Stop robot")
                motion_num = "stop"
                with variables.lock:
                    variables.automatic_control = 0
                robot.send_motion_cmd(motion_num)

            elif motion_num == const.CALIBRATE:
                print("starting calibrate")
                calibrator_thread = threading.Thread(
                    target=object_detector.calibrate_filter)
                with variables.lock:
                    variables.exit_calibrate = 0
                calibrator_thread.start()
            elif motion_num == const.CALIBRATE_STOP:
                print("stopping calibrate")
                with variables.lock:
                    variables.exit_calibrate = 1

            elif motion_num == const.DETECT_ON:
                with variables.lock:
                    variables.automatic_control = 1
                print("detect start")
            elif motion_num == const.DETECT_OFF:
                with variables.lock:
                    variables.automatic_control = 0
                print("detect stop")

            elif motion_num == const.DEBUG_ON:
                debug.debug_cam = 1
                debug.debug_circles = 1
                debug.debug_cycles = 1
                debug.debug_robot = 1
                print("debug on")
            elif motion_num == const.DEBUG_OFF:
                debug.debug_cam = 0
                debug.debug_circles = 0
                debug.debug_cycles = 0
                debug.debug_robot = 0
                print("debug off")

            elif motion_num == const.EXIT1 or motion_num == const.EXIT2:
                with variables.lock:
                    variables.exit_gen = 1
                print("exiting")
                break
            else:
                try:
                    motion_num = int(motion_num)
                except Exception as e:
                    print("Error in motion conversion\n error is ", e)
                    motion_num = "not valid"

                if motion_num == "not valid":
                    pass
                elif motion_num < 0:
                    with variables.lock:
                        variables.exit_code = 1
                    print("exiting")
                    break
                elif motion_num in variables.motion_dictionary:
                    robot.send_motion_cmd(motion_num)
                else:
                    print("Invalid option")
    except Exception as e:
        print("Main program exiting with exception: \n", e)

    finally:
        with variables.lock:
            variables.exit_gen = 1


if __name__ == "__main__":
    main()

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
import variables
import const
import circle_detection
import robot_control
import debug
import control_functions


def main():
    # Create objects to control robot and circle detection/calibration
    object_detector = circle_detection.ObjectDetection()
    robot = robot_control.Robot()

    # Create sub threads
    object_detector_thread = (
        threading.Thread(target=object_detector.object_detection, ))
    automatic_robot_thread = threading.Thread(
        target=robot.automatic_control)

    # Start sub threads before initiating manual control
    automatic_robot_thread.start()
    object_detector_thread.start()

    try:
        # Loop until exit flag set to True(1)
        while not variables.exit_gen:
            # Get users desired action
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
                # Make sure an integer was entered then send command if valid
                control_functions.send_command(
                    robot, motion_num, variables.full_motion_dictionary)

            # Create keyboard remote
            elif motion_num == const.REMOTE:
                alert_window = control_functions.AlertWindow("remote")
                alert_window.output_window("Enter a key")
                # Loop until exit flag set to 1
                while not variables.exit_gen:
                    # get users command
                    command = cv2.waitKey(0)

                    # Stop robot motion
                    if command == const.STOP_R:
                        message = "Robot stop"
                        alert_window.output_window(message)
                        control_functions.stop_motion(robot)

                    # Enable and disable detection motion command
                    elif command == const.DETECT_ON_R:
                        message = "detect on"
                        alert_window.output_window(message)
                        control_functions.detect_on()
                    elif command == const.DETECT_OFF_R:
                        message = "detect off"
                        alert_window.output_window(message)
                        control_functions.detect_off()

                    # Move the robot
                    elif command == const.FORWARD_R:
                        message = "forward"
                        alert_window.output_window(message)
                        control_functions.send_command(robot, 15)
                    elif command == const.BACKWARD_R:
                        message = "backward"
                        alert_window.output_window(message)
                        control_functions.send_command(robot, 16)
                    elif command == const.LEFT_R:
                        message = "left"
                        alert_window.output_window(message)
                        control_functions.send_command(robot, 17)
                    elif command == const.RIGHT_R:
                        message = "right"
                        alert_window.output_window(message)
                        control_functions.send_command(robot, 18)

                    # Turn the robot
                    elif command == const.TURN_R:
                        message = "turn"
                        alert_window.output_window(message)
                        command = cv2.waitKey(0)
                        if command == const.LEFT_R:
                            message = "turn left"
                            alert_window.output_window(message)
                            control_functions.send_command(robot, 19)
                        elif command == const.RIGHT_R:
                            message = "turn right"
                            alert_window.output_window(message)
                            control_functions.send_command(robot, 20)
                        else:
                            message = "invalid turn"
                            alert_window.output_window(message)

                    # Exit program
                    elif command == const.EXIT_R:
                        control_functions.send_command(robot, -1)

                    # Close remote
                    elif command == const.CLOSE_R:
                        break
                    else:
                        message = "invalid option"
                        alert_window.output_window(message)
                # Close window object (close opencv window)
                del alert_window

            # Print dictionary
            elif motion_num == const.DICTIONARY:
                for key in variables.motion_dictionary:
                    print(key, " : ", variables.motion_dictionary[key])

            # Stop robot current motion
            elif motion_num == const.STOP1 or motion_num == const.STOP2:
                control_functions.stop_motion(robot)

            # Start or stop calibration
            elif motion_num == const.CALIBRATE:
                # Ensure calibrator thread is not already active
                if ("calibrator_thread" not in locals() or
                        not calibrator_thread.isAlive()):
                    print("starting calibrate")
                    calibrator_thread = threading.Thread(
                        target=object_detector.calibrate_filter)
                    with variables.lock:
                        variables.exit_calibrate = 0
                    calibrator_thread.start()
                else:
                    print("calibrate already active")
            elif motion_num == const.CALIBRATE_STOP:
                print("stopping calibrate")
                with variables.lock:
                    variables.exit_calibrate = 1

            # Enable or disable ball detection from sending motion command
            elif motion_num == const.DETECT_ON:
                control_functions.detect_on()
            elif motion_num == const.DETECT_OFF:
                control_functions.detect_off()

            # Turn debug verbose on or off
            elif motion_num == const.DEBUG_ON:
                debug.debug_on()
            elif motion_num == const.DEBUG_OFF:
                debug.debug_off()

            # Create exit condition
            elif motion_num == const.EXIT1 or motion_num == const.EXIT2:
                control_functions.exit_program()
            else:
                control_functions.send_command(robot, motion_num)
    except Exception as e:
        print("Main program exiting with exception: \n", e)

    finally:
        with variables.lock:
            # Set exit flag for all threads
            variables.exit_gen = 1
        del robot
        del object_detector


if __name__ == "__main__":
    main()

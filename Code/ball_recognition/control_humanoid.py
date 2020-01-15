import threading
import cv2

# Project specific modules
from misc import Generic
from variables import ExitControl, RobotCom
from constants import Locks, KeyWordControl, R_Control, DICTS
from circle_detection import ObjectDetector
from robot_control import Robot
from debug import Debug
from control_functions import Funcs, AlertWindow


def control_humanoid():
    robot = Robot.get_inst(1)
    object_detector = ObjectDetector()
    try:
        # Loop until exit flag set to True(1)
        while not ExitControl.gen:
            # Get users desired action
            motion_num = Generic.get_int("Enter motion num: ")
            # Give access to full range of motions
            if motion_num == KeyWordControl.FULL_CONTROL:
                print("full control")
                motion_num = Generic.get_int("Enter motion num: ")
                # Print dictionary
                if motion_num == KeyWordControl.DICTIONARY:
                    for key in DICTS.HUMANOID_FULL:
                        print("{} :{} ".format(
                            key, DICTS.HUMANOID_FULL[key]))
                        motion_num = Generic.get_int("Enter motion num: ")
                if motion_num in DICTS.HUMANOID_FULL:
                    robot.play_rcb4_motion(DICTS.HUNDRED_NUM[motion_num])

            # Create keyboard remote
            elif motion_num == KeyWordControl.REMOTE:
                alert_window = AlertWindow("remote")
                alert_window.output("Enter a key")
                ExitControl.remote = 0
                # Loop until exit flag set to 1
                while not ExitControl.remote:
                    # get users command
                    command = cv2.waitKey(0)

                    # Stop robot motion
                    if command == KeyWordControl.STOP:
                        message = "Robot stop"
                        alert_window.output(message)
                        robot.play_rcb4_motion(DICTS.HUNDRED_NUM[1])

                    # Enable and disable detection motion command
                    elif command == R_Control.DETECT_ON:
                        message = "detect on"
                        alert_window.output(message)
                        Funcs.detect_on()
                    elif command == R_Control.DETECT_OFF:
                        message = "detect off"
                        alert_window.output(message)
                        Funcs.detect_off()

                    # Move the robot
                    elif command == R_Control.FORWARD:
                        message = "forward"
                        alert_window.output(message)
                        robot.play_rcb4_motion(
                            DICTS.HUNDRED_NUM[15])
                    elif command == R_Control.BACKWARD:
                        message = "backward"
                        alert_window.output(message)
                        robot.play_rcb4_motion(DICTS.HUNDRED_NUM[16])
                    elif command == R_Control.LEFT:
                        message = "left"
                        alert_window.output(message)
                        robot.play_rcb4_motion(DICTS.HUNDRED_NUM[17])
                    elif command == R_Control.RIGHT:
                        message = "right"
                        alert_window.output(message)
                        robot.play_rcb4_motion(DICTS.HUNDRED_NUM[18])

                    # Turn the robot
                    elif command == R_Control.TURN:
                        message = "turn"
                        alert_window.output(message)
                        command = cv2.waitKey(0)
                        if command == R_Control.LEFT:
                            message = "turn left"
                            alert_window.output(message)
                            robot.play_rcb4_motion(DICTS.HUNDRED_NUM[19])
                        elif command == R_Control.RIGHT:
                            message = "turn right"
                            alert_window.output(message)
                            robot.play_rcb4_motion(DICTS.HUNDRED_NUM[20])
                        else:
                            message = "invalid turn"
                            alert_window.output(message)

                    # Exit program
                    elif command == R_Control.EXIT:
                        ExitControl.gen = 1
                        ExitControl.remote = 1
                        print("exiting")

                    # Close remote
                    elif command == R_Control.CLOSE:
                        ExitControl.remote = 1
                    else:
                        message = "invalid option"
                        alert_window.output(message)
                # Close window object (close opencv window)
                del alert_window

            # Print dictionary
            elif motion_num == KeyWordControl.DICTIONARY:
                for key in DICTS.HUMANOID_MOTION:
                    print(key, " : ", DICTS.HUMANOID_MOTION[key])

            # Stop robot current motion
            elif (motion_num == KeyWordControl.STOP1
                  or motion_num == KeyWordControl.STOP2):
                robot.play_rcb4_motion(DICTS.HUNDRED_NUM[1])

            # Start calibration
            elif motion_num == KeyWordControl.CALIBRATE:
                # Ensure calibrator thread is not already active
                if ("calibrator_thread" not in locals() or
                        not calibrator_thread.is_alive()):
                    print("starting calibrate")
                    calibrator_thread = threading.Thread(
                        target=object_detector.calibrate_filter)
                    with Locks.CAM_LOCK:
                        ExitControl.calibrate = 0
                    calibrator_thread.start()
                else:
                    print("calibrate already active")
            # Stop Calibration
            elif motion_num == KeyWordControl.CALIBRATE_STOP:
                print("stopping calibrate")
                with Locks.CAM_LOCK:
                    ExitControl.calibrate = 1

            # Enable or disable ball detection from sending motion command
            elif motion_num == KeyWordControl.DETECT_ON:
                Funcs.detect_on()
            elif motion_num == KeyWordControl.DETECT_OFF:
                Funcs.detect_off()

            # Turn debug verbose on or off
            elif motion_num == KeyWordControl.DEBUG_ON:
                Debug.debug_on()
            elif motion_num == KeyWordControl.DEBUG_OFF:
                Debug.debug_off()

            # Create exit condition
            elif (motion_num == KeyWordControl.EXIT1
                  or motion_num == KeyWordControl.EXIT2):
                Funcs.exit_program()
            else:
                if motion_num in DICTS.HUMANOID_MOTION:
                    robot.play_rcb4_motion(DICTS.HUNDRED_NUM[motion_num])
    except Exception as e:
        print("Main program exiting with exception: \n", e)

    finally:
        with Locks.gen:
            # Set exit flag for all threads
            ExitControl.gen = 1
        del robot
        del object_detector

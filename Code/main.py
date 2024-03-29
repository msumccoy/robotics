"""
Kuwin Wyke
Midwestern State University
"""
# import multiprocessing
import threading
import logging
import time

import log_set_up_and_funcs  # This must Always be the first custom module imported
# Custom Modules  ############################################################
from camera import Camera
from gui import gui_main
from robot_control import Robot
from config import Conf
from enums import RobotType
from misc import pretty_time
from socket_server import SocketServer


def start_camera(robot_type):
    # Camera must start and operate in independent thread for OpenCV to
    # control windows as only one thread can open and operate OpenCV windows
    cam = Camera.get_inst(
        robot_type,
        cam_num=-1,
        disp=True,
        # record=True,
        # take_pic=True,
        # set_up=True,
        split_img=True,
    )
    try:
        cam.start_recognition()
    finally:
        cam.close()


def main():
    # TODO: Create
    #   - GUI
    #       - Should run in secondary daemon process while robot and camera
    #         run in main process
    #       - Will connect via socket
    start = time.time()
    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
    main_logger.info(f"Main function starting on version {Conf.VERSION}")
    robot_type = RobotType.HUMAN
    # robot_type = RobotType.SPIDER

    # Set up all class instances #############################################
    robot = Robot.get_inst(
        robot_type,
        enable_auto=False
    )
    cam_starter = threading.Thread(
        target=start_camera, args=(robot_type,)
    )
    cam_starter.start()
    time.sleep(.1)
    cam = Camera.get_inst(robot_type)
    # # Socket thread is not needed without GUI being active
    # socket_server = SocketServer(robot_type)
    # socket_thread = threading.Thread(target=socket_server.start, daemon=True)
    # socket_thread.start()
    ##########################################################################
    # Start gui if wanted on same system######################################
    # TODO: Set up GUI process
    #  - Get image from camera to gui (hopefully via socket)
    # start_gui = True
    # # start_gui = False
    # if start_gui:
    #     gui_proc = multiprocessing.Process(target=gui_main, daemon=True)
    #     gui_proc.start()
    ##########################################################################

    i = 0
    while cam.is_connected and not cam.is_profile_setup:
        time.sleep(1)
        i += 1
        if i % 30 == 0:
            print("Main thread waiting for camera to complete setup")

    try:
        robot.manual_control()
    finally:
        robot.close()

    main_logger.info(
        f"Program completed after running for {pretty_time(start)}\n"
    )


if __name__ == "__main__":
    main()

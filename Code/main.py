"""
Kuwin Wyke
Midwestern State University
"""
import threading
import logging
import time

import log_set_up  # This must Always be the first custom module imported
# Custom Modules  ############################################################
from camera import Camera
from robot_control import Robot
from config import Conf
from enums import RobotType, LensType
from misc import pretty_time, manual_ender
from variables import ExitControl
from gui import GUI


def cam_starter(robot_type):
    cam = Camera.get_inst(
        robot_type,
        # cam_num=2,
        # lens_type=LensType.DOUBLE,
        # record=True,
        # take_pic=True,
    )
    try:
        cam.start_recognition()
    finally:
        cam.close()


def main():
    start = time.time()
    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
    main_logger.info(f"Main function starting on version {Conf.VERSION}")
    robot_type = RobotType.SPIDER

    cam_thread = threading.Thread(target=cam_starter, args=(robot_type,))
    cam_thread.start()

    cam = Camera.get_inst(robot_type)
    auto_robot_thread = threading.Thread(target=cam.control_robot)
    auto_robot_thread.start()

    robot = Robot.get_inst(robot_type)
    manual_robot_thread = threading.Thread(
        target=robot.manual_control, daemon=True
    )
    manual_robot_thread.start()

    gui = GUI(robot_type)
    gui.start()

    time.sleep(.5)
    cam.close()
    robot.close()

    main_logger.info(
        f"Program completed after running for {pretty_time(start)}\n"
    )


if __name__ == "__main__":
    main()

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


def main():
    # TODO: Create
    # TODO: separate each section to run independently
    #   - Robot
    #       - CLI interface should be in the main thread
    #   - Camera
    #       - Recognition  should be in sub thread
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
    # Start setting robot to run independently (will add camera control next)
    robot = Robot.get_inst(robot_type, enable_auto=False)
    cam = Camera.get_inst(
        robot_type,
        # cam_num=2,
        # record=True,
        # take_pic=True,
    )
    ##########################################################################

    try:
        robot.manual_control()
    finally:
        robot.close()

    main_logger.info(
        f"Program completed after running for {pretty_time(start)}\n"
    )


if __name__ == "__main__":
    main()

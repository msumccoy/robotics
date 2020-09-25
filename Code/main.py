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


def main():
    start = time.time()
    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
    main_logger.info(f"Main function starting on version {Conf.VERSION}")

    robot_type = RobotType.HUMAN
    robot = Robot.get_inst(robot_type)
    cam = Camera.get_inst(
        robot_type,
        # cam_num=2,
        lens_type=LensType.DOUBLE,
        record=True,
        take_pic=True,
        is_test=True
    )

    cam_thread = threading.Thread(target=cam.start_recognition)
    manual_robot_thread = threading.Thread(
        target=robot.manual_control
    )

    cam_thread.start()
    manual_robot_thread.start()

    cam_thread.join()
    manual_robot_thread.join()

    cam.close()
    robot.close()
    main_logger.info(
        f"Program completed after running for {pretty_time(start)}\n"
    )


if __name__ == "__main__":
    main()

"""
Kuwin Wyke
Midwestern State University

This module is use to set up the logging before any other modules attempt to
log any information. Consequently, this must module must be the first import
at the start of the program
"""
import logging

from config import Conf


formatter = logging.Formatter(Conf.FORMAT)

# Set up main logger  ########################################################
main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
main_logger.setLevel(logging.DEBUG)

main_file_handler = logging.FileHandler(Conf.LOG_MAIN_FILE)
main_file_handler.setFormatter(formatter)
main_file_handler.setLevel(Conf.LOG_MAIN_FILE_LEVEL)

main_stream_handler = logging.StreamHandler()
main_stream_handler.setFormatter(formatter)
main_stream_handler.setLevel(Conf.LOG_MAIN_STREAM_LEVEL)

main_logger.addHandler(main_file_handler)
main_logger.addHandler(main_stream_handler)

# Set up camera logger  ######################################################
cam_logger = logging.getLogger(Conf.LOG_CAM_NAME)
cam_logger.setLevel(logging.DEBUG)

cam_file_handler = logging.FileHandler(Conf.LOG_CAM_FILE)
cam_file_handler.setFormatter(formatter)
cam_file_handler.setLevel(Conf.LOG_CAM_FILE_LEVEL)

cam_stream_handler = logging.StreamHandler()
cam_stream_handler.setFormatter(formatter)
cam_stream_handler.setLevel(Conf.LOG_CAM_STREAM_LEVEL)

main_logger.addHandler(cam_file_handler)
main_logger.addHandler(cam_stream_handler)

# Set up robot logger  #######################################################
robot_logger = logging.getLogger(Conf.LOG_ROBOT_NAME)
robot_logger.setLevel(logging.DEBUG)

robot_file_handler = logging.FileHandler(Conf.LOG_ROBOT_FILE)
robot_file_handler.setFormatter(formatter)
robot_file_handler.setLevel(Conf.LOG_ROBOT_FILE_LEVEL)

robot_stream_handler = logging.StreamHandler()
robot_stream_handler.setFormatter(formatter)
robot_stream_handler.setLevel(Conf.LOG_ROBOT_STREAM_LEVEL)

robot_logger.addHandler(robot_file_handler)
robot_logger.addHandler(robot_stream_handler)

"""
Kuwin Wyke
Midwestern State University

This module is use to set up the logging before any other modules attempt to
log any information. Consequently, this must module must be the first import
at the start of the program
"""
import logging
from logging import handlers

from config import Conf

# TODO: limit the number of logs of a certain type go to log file to prevent flooding

formatter = logging.Formatter(Conf.FORMAT, Conf.FORMAT_DATE)
formatter_terminal = logging.Formatter(Conf.FORMAT_TERMINAL, Conf.FORMAT_DATE)

# Set up main logger  ########################################################
main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
main_logger.setLevel(logging.DEBUG)

main_file_handler = handlers.RotatingFileHandler(
    Conf.LOG_MAIN_FILE, maxBytes=Conf.MAX_BYTES, backupCount=Conf.BACKUP_COUNT
)
main_file_handler.setFormatter(formatter)
main_file_handler.setLevel(Conf.LOG_MAIN_FILE_LEVEL)

main_stream_handler = logging.StreamHandler()
main_stream_handler.setFormatter(formatter_terminal)
main_stream_handler.setLevel(Conf.LOG_MAIN_STREAM_LEVEL)

main_logger.addHandler(main_file_handler)
main_logger.addHandler(main_stream_handler)

# Set up camera logger  ######################################################
cam_logger = logging.getLogger(Conf.LOG_CAM_NAME)
cam_logger.setLevel(logging.DEBUG)

cam_file_handler = handlers.RotatingFileHandler(
    Conf.LOG_CAM_FILE, maxBytes=Conf.MAX_BYTES, backupCount=Conf.BACKUP_COUNT
)
cam_file_handler.setFormatter(formatter)
cam_file_handler.setLevel(Conf.LOG_CAM_FILE_LEVEL)

cam_stream_handler = logging.StreamHandler()
cam_stream_handler.setFormatter(formatter_terminal)
cam_stream_handler.setLevel(Conf.LOG_CAM_STREAM_LEVEL)

cam_logger.addHandler(cam_file_handler)
cam_logger.addHandler(cam_stream_handler)

# Set up robot logger  #######################################################
robot_logger = logging.getLogger(Conf.LOG_ROBOT_NAME)
robot_logger.setLevel(logging.DEBUG)

robot_file_handler = handlers.RotatingFileHandler(
    Conf.LOG_ROBOT_FILE, maxBytes=Conf.MAX_BYTES, backupCount=Conf.BACKUP_COUNT
)
robot_file_handler.setFormatter(formatter)
robot_file_handler.setLevel(Conf.LOG_ROBOT_FILE_LEVEL)

robot_stream_handler = logging.StreamHandler()
robot_stream_handler.setFormatter(formatter_terminal)
robot_stream_handler.setLevel(Conf.LOG_ROBOT_STREAM_LEVEL)

robot_logger.addHandler(robot_file_handler)
robot_logger.addHandler(robot_stream_handler)

# Set up robot logger  #######################################################
socket_logger = logging.getLogger(Conf.LOG_SOCKET_NAME)
socket_logger.setLevel(logging.DEBUG)

socket_file_handler = handlers.RotatingFileHandler(
    Conf.LOG_SOCKET_FILE, maxBytes=Conf.MAX_BYTES, backupCount=Conf.BACKUP_COUNT
)
socket_file_handler.setFormatter(formatter)
socket_file_handler.setLevel(Conf.LOG_SOCKET_FILE_LEVEL)

socket_stream_handler = logging.StreamHandler()
socket_stream_handler.setFormatter(formatter_terminal)
socket_stream_handler.setLevel(Conf.LOG_SOCKET_STREAM_LEVEL)

socket_logger.addHandler(socket_file_handler)
socket_logger.addHandler(socket_stream_handler)

# Set up gui logger  #########################################################
# GUI logger will be set up in gui.py

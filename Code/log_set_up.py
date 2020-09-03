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

main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
main_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(Conf.LOG_FILE)
file_handler.setFormatter(formatter)
file_handler.setLevel(Conf.LOG_FILE_LEVEL)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(Conf.LOG_STREAM_LEVEL)

main_logger.addHandler(file_handler)
main_logger.addHandler(stream_handler)

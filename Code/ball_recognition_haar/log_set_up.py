"""
Kuwin Wyke
Midwestern State University

This module is use to set up the logging before any other modules attempt to
log any information. Consequently, this must module must be the first import
at the start of the program
"""
import logging

from ball_recognition_haar.config import Log


logger = logging.getLogger(Log.NAME)
logger.setLevel(Log.BASE_LEVEL)
formatter = logging.Formatter(Log.FORMAT)

file_handler = logging.FileHandler(Log.LOG_FILE)
file_handler.setFormatter(formatter)
file_handler.setLevel(Log.FILE_LEVEL)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)

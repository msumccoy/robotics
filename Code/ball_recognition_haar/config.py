"""
Kuwin Wyke
Midwestern State University

This module contains the configuration settings for the project
"""
import cv2
import logging
from string import Template


class Conf:
    BALL_WINDOW_MAIN = "Dual lens output"
    BALL_WINDOW_LEFT = "Left lens output"
    BALL_WINDOW_RIGHT = "Right lens output"
    CASCADE_FILE = "cascade_files/tennis_ball_20x20_stage14_3500samples.xml"
    BALL_DETECTOR = cv2.CascadeClassifier(CASCADE_FILE)


class Templates:
    WARN_CAM_TYPE = Template(
        "Camera view size error detected. Ensure you are using a dual lens "
        "camera"
    )


class Log:
    NAME = "main_log"
    LOG_ROOT = "logs/"
    LOG_FILE = LOG_ROOT + "main.log"
    BASE_LEVEL = logging.INFO
    FILE_LEVEL = logging.INFO
    FORMAT = "%(asctime)s: %(levelname)s: %(message)s"
    WRITE_FREQUENCY = 30

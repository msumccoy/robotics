""" Kuwin Wyke
Midwestern State University

This file is just used to store configuration constants for the other sections
of this program.
"""
import cv2


class Conf:
    IMG_PATH = "labeled"
    IMG_PATH_FILE = "orig_images"
    IMG_PATH_CROP = "cropped_images"
    LABEL_FILE = IMG_PATH + "/info.lst"
    CROP_SIZE = 50
    MAX_IMG_WIDTH = 700
    CAM_PREFIX = "_cam"
    FILE_PREFIX = "_file"


class CV_Window:
    # Name of main window
    WINDOW_NAME = "Picture to label"
    # Window name for instructions
    REQUEST_WINDOW = "Request window"
    REQUEST_MESSAGE = (
        "Please enter the number of items in the image (from 1 to 9)"
    )
    ACCEPT_MESSAGE = (
        "Press 'Esc' to exit, "
        "'r' to restart labeling , 'x' to skip or any other key to save"
    )
    MESSAGE_WINDOW = "Message Window"
    ORG = (0, 15)
    FONT = cv2.QT_FONT_NORMAL
    FONT_SCALE = .75
    COLOR = (3, 252, 78)
    COLOR2 = (3, 252, 3)
    THICKNESS = 1

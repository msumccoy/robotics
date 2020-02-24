""" Kuwin Wyke
Midwestern State University

This file is just used to store configuration constants for the other sections
of this program.
"""
import cv2


class Conf:
    IMG_PATH = "info/"
    RAW_LABEL_FILE = "raw_pos.txt"
    FULL_LABEL_FILE = "info.lst"
    FINAL_POS_SIZE = 50


class CamConf:
    WIDTH = 640
    HEIGHT = 380
    # Target length of square after resizing positive image
    RESIZE = 300


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
    THICKNESS = 1

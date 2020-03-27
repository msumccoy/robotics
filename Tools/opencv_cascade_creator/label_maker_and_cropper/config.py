""" Kuwin Wyke
Midwestern State University

This file is just used to store configuration constants for the other sections
of this program.
"""
import cv2


class Conf:
    VERSION = 2.0
    LABELED_IMG_FOLDER = "labeled"
    ORIG_IMG_FOLDER = "orig_images"
    CROPPED_IMG_FOLDER = "cropped_images"
    DELETED_IMG_FOLDER = "images_to_delete"
    SKIP_FOLDER = "skipped"
    ORIG_AFTER_LABEL = "originals_after_labeling"
    LABEL_FILE = LABELED_IMG_FOLDER + "/info.lst"
    CROP_SIZE = 50
    # Max width before image resizing
    MAX_IMG_WIDTH = 700


class CV_Window:
    # Name of main window
    MAIN_WINDOW = f"Image labeler version {Conf.VERSION}"
    FONT = cv2.QT_FONT_NORMAL
    FONT_SCALE = .75
    COLOR = (3, 252, 78)
    COLOR2 = (245, 200, 66)
    COLOR3 = (255, 255, 255)
    COLOR4 = (0, 0, 0)
    THICKNESS = 1

    # Window name for instructions
    INFO_WINDOW = "INFO WINDOW"
    INFO_WINDOW_SIZE = (700, 700, 3)
    LINES = [
        "Press: ",  # Line 1
        "  'Space bar' to save bounding boxes",  # Line 2
        "  'Esc' or 's' to save info.lst file",  # Line 3
        "  'r' to restart labeling",  # Line 4
        "  'x' to skip image",  # Line 5
        "  'd' to delete current image",  # Line 6
        "  'b' to activate/deactivate section blocker",  # Line 7
    ]

    X_ORG = 0
    Y_ORG = 30
    NAME_ORG = (X_ORG, Y_ORG)
    ORIGINS = [
        (X_ORG, Y_ORG),  # Line 1
        (X_ORG, Y_ORG * 2),  # Line 2
        (X_ORG, Y_ORG * 3),  # ECT.
        (X_ORG, Y_ORG * 4),
        (X_ORG, Y_ORG * 5),
        (X_ORG, Y_ORG * 6),
        (X_ORG, Y_ORG * 7),
    ]

    INFO_LIST = zip(LINES, ORIGINS)

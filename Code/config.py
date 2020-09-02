"""
Kuwin Wyke
Midwestern State University

This module contains the configuration settings for the project
"""
import json
import logging
import os
import threading
from string import Template

import cv2
import serial

config_file = "/home/kuwin/file2.json"
with open(config_file) as file:
    config = json.load(file)


class Conf:
    # VERSION = major_change.minor_change
    VERSION = 2.0
    PATH_ROOT = config["path"] + "/"
    ##########################################################################
    # Templates  #############################################################
    ##########################################################################
    WARN_CAM_TYPE = Template(
        "Camera view size error detected. Ensure you are using a dual lens "
        "camera"
    )

    ##########################################################################
    # Robot Settings  ########################################################
    ##########################################################################
    # Serial port connection settings
    HUMANOID_PORT = config["humanoid_port"]
    SPIDER_PORT = config["spider_port"]
    BAUDRATE = 9600
    BYTESIZE = serial.EIGHTBITS
    PARITY = serial.PARITY_EVEN
    STOPBITS = serial.STOPBITS_ONE
    SER_TIMEOUT = 1

    PORT_TIME_OUT = 20  # How long before we give up on trying to connect

    # Movement control dictionaries  #########################################
    HUMANOID_FULL = {  # Full dictionary with all motions in Heart2Heart
        0: "Bow -- not working!!!",
        1: "Home position",
        2: "Waving",
        3: "stretch",
        4: "Craw like motion",
        5: "Dance (hard on servos)",
        6: "Don't know",
        7: "Clap 1",
        8: "Clap 2",
        9: "Push ups",
        10: "Don't know (hard on servos)",
        11: "Jump 3 times (worst on servo)",
        12: "Get off the ground (direction sensing)",
        13: "Get off the ground (face down)",
        14: "Get off the ground (face up)",
        15: "Move forward 5 steps (slowly)",
        16: "Move backward 5 steps (slowly)",
        17: "Move left 5 steps (slowly)",
        18: "Move right 5 steps (slowly)",
        19: "Turn left (5 step turn)",
        20: "Turn right (5 step turn)",
        21: "Move forward 5 steps (fast but more unstable)",
        22: "Move backward 5 steps (fast but more unstable)",
        23: "Move left 5 steps (fast but more unstable)",
        24: "Move right 5 steps (fast but more unstable)",
        25: "Kick forward with left foot",
        26: "Kick forward with right foot",
        27: "*not sure* kick with left foot",
        28: "*not sure* kick with right foot",
        29: "Kick back with left foot",
        30: "Kick back with right foot",
        31: "Empty",
        32: "Defense (fighting)",
        33: "Punch forward (fighting)",
        34: "Left punch (fighting)",
        35: "Right punch (fighting)",
        36: "pose",
        37: "pose",
        38: "Empty",
        39: "cannot use",
        40: "cannot use",
        41: "cannot use",
        42: "cannot use",
        43: "cannot use",
        44: "cannot use",
        45: "cannot use",
        46: "cannot use",
        47: "cannot use",
        48: "cannot use",
        49: "cannot use",
        50: "cannot use",
    }
    HUMANOID_MOTION = {
        # Condensed dictionary for all accepted movements
        1: "Home position",
        2: "Waving",
        3: "stretch",
        4: "Craw like motion",
        7: "Clap 1",
        8: "Clap 2",
        9: "Push ups",
        12: "Get off the ground (direction sensing)",
        13: "Get off the ground (face down)",
        14: "Get off the ground (face up)",
        15: "Move forward 5 steps (slowly)",
        16: "Move backward 5 steps (slowly)",
        17: "Move left 5 steps (slowly)",
        18: "Move right 5 steps (slowly)",
        19: "Turn left (5 step turn)",
        20: "Turn right (5 step turn)",
        21: "Move forward 5 steps (fast but more unstable)",
        22: "Move backward 5 steps (fast but more unstable)",
        23: "Move left 5 steps (fast but more unstable)",
        24: "Move right 5 steps (fast but more unstable)",
        25: "Kick forward with left foot",
        26: "Kick forward with right foot",
        27: "*not sure* kick with left foot",
        28: "*not sure* kick with right foot",
        29: "Kick back with left foot",
        30: "Kick back with right foot",
        36: "pose",
        37: "pose",
    }

    SPIDER_FULL = {
        0: "up and down",
        1: "forward slightly",
        2: "back slightly",
        3: "turn left (fast slight turn)",
        4: "turn right (fast slight turn)",
        5: "forward 6 steps (slow)",
        6: "back 6 steps (slow)",
        7: "turn left (slow mid turn)",
        8: "turn right (slow mid turn)",
        9: "slow prance",
        # Dance 1: up on hind-legs and wave; forward slightly; back slightly;
        #          wiggle; up on hind-legs move front legs up and down
        10: "dance 1",
        # up and down several times; fast prance; wiggle
        11: "dance 2",
        12: "turn right (slow big turn)",
        13: "turn left (slow big turn)",
        14: "forward then back (fast)",
        15: "dance (wiggle then remain mid height)",
        16: "slow wiggle",
        17: "stand mid height",
        18: "forward 3 steps (slow remain mid height)",
        19: "back 3 steps (slow remain mid height)",
        20: "forward continuously",
        21: "turn right continuously",
        22: "turn left continuously",
        23: "forward continuously",
        24: "",
        25: "",
        26: "",
        27: "",
        28: "",
        29: "wave front right paw (continuous?)",
        30: "",
        39: "Stance (the legs up"
    }

    # Hex Constants  #########################################################
    HEX_STOP = b"\x09\x00\x02\x00\x00\x00\x10\x83\x9e"
    HEX_RESET = (
        b"\x11\x00\x02\x02\x00\x00\x4b\x04"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x64"
    )
    HEX_RESUME = b"\x09\x00\x02\x00\x00\x00\x13\x83\xa1"

    HEX_ACK_COMMAND = b"\x04\xfe\x06\x08"
    HEX_GET_OPTIONS = b"\x0a\x00\x20\x00\x00\x00\x00\x00\x02\x2c"

    HEX_HUNDRED_NUM = [
        b"\x07\x0c\x80\x0b\x00\x00\x9e",
        b"\x07\x0c\x80\x13\x00\x00\xa6",
        b"\x07\x0c\x80\x1b\x00\x00\xae",
        b"\x07\x0c\x80\x23\x00\x00\xb6",
        b"\x07\x0c\x80\x2b\x00\x00\xbe",
        b"\x07\x0c\x80\x33\x00\x00\xc6",
        b"\x07\x0c\x80\x3b\x00\x00\xce",
        b"\x07\x0c\x80\x43\x00\x00\xd6",
        b"\x07\x0c\x80\x4b\x00\x00\xde",
        b"\x07\x0c\x80\x53\x00\x00\xe6",
        b"\x07\x0c\x80\x5b\x00\x00\xee",
        b"\x07\x0c\x80\x63\x00\x00\xf6",
        b"\x07\x0c\x80\x6b\x00\x00\xfe",
        b"\x07\x0c\x80\x73\x00\x00\x06",
        b"\x07\x0c\x80\x7b\x00\x00\x0e",
        b"\x07\x0c\x80\x83\x00\x00\x16",
        b"\x07\x0c\x80\x8b\x00\x00\x1e",
        b"\x07\x0c\x80\x93\x00\x00\x26",
        b"\x07\x0c\x80\x9b\x00\x00\x2e",
        b"\x07\x0c\x80\xa3\x00\x00\x36",
        b"\x07\x0c\x80\xab\x00\x00\x3e",
        b"\x07\x0c\x80\xb3\x00\x00\x46",
        b"\x07\x0c\x80\xbb\x00\x00\x4e",
        b"\x07\x0c\x80\xc3\x00\x00\x56",
        b"\x07\x0c\x80\xcb\x00\x00\x5e",
        b"\x07\x0c\x80\xd3\x00\x00\x66",
        b"\x07\x0c\x80\xdb\x00\x00\x6e",
        b"\x07\x0c\x80\xe3\x00\x00\x76",
        b"\x07\x0c\x80\xeb\x00\x00\x7e",
        b"\x07\x0c\x80\xf3\x00\x00\x86",
        b"\x07\x0c\x80\xfb\x00\x00\x8e",
        b"\x07\x0c\x80\x03\x01\x00\x97",
        b"\x07\x0c\x80\x0b\x01\x00\x9f",
        b"\x07\x0c\x80\x13\x01\x00\xa7",
        b"\x07\x0c\x80\x1b\x01\x00\xaf",
        b"\x07\x0c\x80\x23\x01\x00\xb7",
        b"\x07\x0c\x80\x2b\x01\x00\xbf",
        b"\x07\x0c\x80\x33\x01\x00\xc7",
        b"\x07\x0c\x80\x3b\x01\x00\xcf",
        b"\x07\x0c\x80\x43\x01\x00\xd7",
        b"\x07\x0c\x80\x4b\x01\x00\xdf",
        b"\x07\x0c\x80\x53\x01\x00\xe7",
        b"\x07\x0c\x80\x5b\x01\x00\xef",
        b"\x07\x0c\x80\x63\x01\x00\xf7",
        b"\x07\x0c\x80\x6b\x01\x00\xff",
        b"\x07\x0c\x80\x73\x01\x00\x07",
        b"\x07\x0c\x80\x7b\x01\x00\x0f",
        b"\x07\x0c\x80\x83\x01\x00\x17",
        b"\x07\x0c\x80\x8b\x01\x00\x1f",
        b"\x07\x0c\x80\x93\x01\x00\x27",
        b"\x07\x0c\x80\x9b\x01\x00\x2f",
        b"\x07\x0c\x80\xa3\x01\x00\x37",
        b"\x07\x0c\x80\xab\x01\x00\x3f",
        b"\x07\x0c\x80\xb3\x01\x00\x47",
        b"\x07\x0c\x80\xbb\x01\x00\x4f",
        b"\x07\x0c\x80\xc3\x01\x00\x57",
        b"\x07\x0c\x80\xcb\x01\x00\x5f",
        b"\x07\x0c\x80\xd3\x01\x00\x67",
        b"\x07\x0c\x80\xdb\x01\x00\x6f",
        b"\x07\x0c\x80\xe3\x01\x00\x77",
        b"\x07\x0c\x80\xeb\x01\x00\x7f",
        b"\x07\x0c\x80\xf3\x01\x00\x87",
        b"\x07\x0c\x80\xfb\x01\x00\x8f",
        b"\x07\x0c\x80\x03\x02\x00\x98",
        b"\x07\x0c\x80\x0b\x02\x00\xa0",
        b"\x07\x0c\x80\x13\x02\x00\xa8",
        b"\x07\x0c\x80\x1b\x02\x00\xb0",
        b"\x07\x0c\x80\x23\x02\x00\xb8",
        b"\x07\x0c\x80\x2b\x02\x00\xc0",
        b"\x07\x0c\x80\x33\x02\x00\xc8",
        b"\x07\x0c\x80\x3b\x02\x00\xd0",
        b"\x07\x0c\x80\x43\x02\x00\xd8",
        b"\x07\x0c\x80\x4b\x02\x00\xe0",
        b"\x07\x0c\x80\x53\x02\x00\xe8",
        b"\x07\x0c\x80\x5b\x02\x00\xf0",
        b"\x07\x0c\x80\x63\x02\x00\xf8",
        b"\x07\x0c\x80\x6b\x02\x00\x00",
        b"\x07\x0c\x80\x73\x02\x00\x08",
        b"\x07\x0c\x80\x7b\x02\x00\x10",
        b"\x07\x0c\x80\x83\x02\x00\x18",
        b"\x07\x0c\x80\x8b\x02\x00\x20",
        b"\x07\x0c\x80\x93\x02\x00\x28",
        b"\x07\x0c\x80\x9b\x02\x00\x30",
        b"\x07\x0c\x80\xa3\x02\x00\x38",
        b"\x07\x0c\x80\xab\x02\x00\x40",
        b"\x07\x0c\x80\xb3\x02\x00\x48",
        b"\x07\x0c\x80\xbb\x02\x00\x50",
        b"\x07\x0c\x80\xc3\x02\x00\x58",
        b"\x07\x0c\x80\xcb\x02\x00\x60",
        b"\x07\x0c\x80\xd3\x02\x00\x68",
        b"\x07\x0c\x80\xdb\x02\x00\x70",
        b"\x07\x0c\x80\xe3\x02\x00\x78",
        b"\x07\x0c\x80\xeb\x02\x00\x80",
        b"\x07\x0c\x80\xf3\x02\x00\x88",
        b"\x07\x0c\x80\xfb\x02\x00\x90",
        b"\x07\x0c\x80\x03\x03\x00\x99",
        b"\x07\x0c\x80\x0b\x03\x00\xa1",
        b"\x07\x0c\x80\x13\x03\x00\xa9",
        b"\x07\x0c\x80\x1b\x03\x00\xb1",
        b"\x07\x0c\x80\x23\x03\x00\xb9",
    ]

    ##########################################################################
    # OpenCV settings  #######################################################
    ##########################################################################
    CV_WINDOW = "Image window"
    CV_WINDOW_LEFT = "Image window left"
    CV_WINDOW_RIGHT = "Image window right"
    CV_FONT = cv2.FONT_HERSHEY_PLAIN
    CV_FONT_SCALE = 2
    CV_TEXT_COLOR = (255, 255, 255)
    CV_LINE_COLOR = (255, 75, 5)
    CV_THICKNESS = 2
    CV_LINE = cv2.LINE_AA
    CV_SIZE = (128, 512, 3)

    CASCADE_ROOT = PATH_ROOT + "cascade_files/"
    CV_CASCADE_FILE = CASCADE_ROOT + "haarcascade_frontalface_alt.xml"
    CV_DETECTOR = cv2.CascadeClassifier(CV_CASCADE_FILE)

    ##########################################################################
    # Camera settings   ######################################################
    ##########################################################################
    VIDEO_ROOT = PATH_ROOT + "videos/"
    if not os.path.exists(VIDEO_ROOT):
        os.mkdir(VIDEO_ROOT)
    CV_VIDEO_FILE = VIDEO_ROOT + "Output_recording.avi"
    CAM_SETTINGS_FILE = PATH_ROOT + "cam_settings.json"
    if not os.path.isfile(CAM_SETTINGS_FILE):
        with open(CAM_SETTINGS_FILE, 'w') as file:
            file.write("{}")

    # CS = camera settings
    CS_DEFAULT = "default"
    CS_FOCAL = "focal_len"
    CS_OBJ_WIDTH = "object_width"
    CS_SCALE = "scale"
    CS_NEIGH = "nearest_neighbour"

    ##########################################################################
    # Log settings  ##########################################################
    ##########################################################################
    LOG_ROOT = PATH_ROOT + "logs/"
    if not os.path.exists(LOG_ROOT):
        os.mkdir(LOG_ROOT)
    LOG_MAIN_NAME = "main"
    LOG_FILE = LOG_ROOT + LOG_MAIN_NAME + ".log"
    LOG_FILE_LEVEL = logging.INFO
    LOG_STREAM_LEVEL = logging.INFO
    FORMAT = "%(asctime)s: %(levelname)s: %(message)s"
    WRITE_FREQUENCY = 30

    ##########################################################################
    # Locks  #################################################################
    ##########################################################################
    HUMANOID_LOCK = threading.Lock()
    SPIDER_LOCK = threading.Lock()

    ##########################################################################
    # Control commands  ######################################################
    ##########################################################################
    # Terminal typed commands
    CMD_FULL_CONTROL = "full"
    CMD_EXIT = "exit"
    CMD_EXIT1 = "e"
    CMD_STOP = "stop"
    CMD_STOP1 = "s"
    CMD_REMOTE = "remote"
    CMD_DICTIONARY = "dict"
    CMD_CALIBRATE = "calibrate"
    CMD_CALIBRATE_STOP = "calibrate stop"
    CMD_DETECT_ON = "detect"
    CMD_DETECT_OFF = "detect stop"

    # Commands for OpenCV window control
    R_CMD_EXIT = ord("e")
    R_CMD_STOP = ord("s")
    R_CMD_DETECT_ON = ord("d")
    R_CMD_DETECT_OFF = ord("o")
    R_CMD_CONTINUOUS_FORWARD = 82
    R_CMD_FORWARD = ord("f")
    R_CMD_BACKWARD = ord("b")
    R_CMD_BACKWARD2 = 84
    R_CMD_LEFT = ord("l")
    R_CMD_LEFT2 = 81
    R_CMD_RIGHT = ord("r")
    R_CMD_RIGHT2 = 83
    R_CMD_TURN = ord("t")
    R_CMD_CLOSE = ord("c")

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

config_file = "/home/pi/file.json"  # This is system specific
# config_file = "/home/kuwin/file2.json"  # This is system specific
with open(config_file) as file:
    config = json.load(file)


class Conf:
    # VERSION = major_change.minor_change
    VERSION = 2.0  # 3.0 to be confirmed after completion
    PATH_ROOT = config["path"]  # Typically: /home/pi/Documents/Code/
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
    # These values are based off of the bluetooth attached location
    HUMANOID_PORT = config["humanoid_port"]  # Typically: /dev/rfcomm1
    SPIDER_PORT = config["spider_port"]  # Typically: /dev/rfcomm2
    BAUDRATE = 9600
    BYTESIZE = serial.EIGHTBITS
    PARITY = serial.PARITY_EVEN
    STOPBITS = serial.STOPBITS_ONE
    SER_TIMEOUT = 1

    PORT_TIME_OUT = 20  # How long before we give up on trying to connect
    MAX_SEARCH_DUR = 60

    # Robot constants
    RBT_MAX_HEAD_LEFT = 180
    RBT_MIN_HEAD_RIGHT = 0
    RBT_MAX_HEAD_BACK = 100
    RBT_MIN_HEAD_FORWARD = 0

    ROBOT_CONTROL = "robot control"
    ROBOT_HEAD = "robot head"
    ROBOT_HEAD_SET_U_D = "robot head set, up and down"
    ROBOT_HEAD_SET_L_R = "robot head set, left and right"

    SEARCH_REST = .5

    # Movement control dictionaries  #########################################
    HUMANOID_FULL = {  # Full dictionary with all motions in Heart2Heart
        0: ["Bow -- not working!!!", 1],
        1: ["Home position", 1],
        2: ["Waving", 1],
        3: ["stretch", 1],
        4: ["Drop to floor and 'cry'", 1],
        5: ["Dance (hard on servos)", 1],
        6: ["Don't know", 1],
        7: ["Clap 1", 1],
        8: ["Clap 2", 1],
        9: ["Push ups", 1],
        10: ["Don't know (hard on servos)", 1],
        11: ["Jump 3 times (worst on servo)", 1],
        12: ["Get off the ground (direction sensing)", 1],
        13: ["Get off the ground (face down)", 1],
        14: ["Get off the ground (face up)", 1],
        15: ["Move forward 5 steps (slowly)", 1],
        16: ["Move backward 5 steps (slowly)", 1],
        17: ["Move left 5 steps (slowly)", 1],
        18: ["Move right 5 steps (slowly)", 1],
        19: ["Turn left (5 step turn)", 1],
        20: ["Turn right (5 step turn)", 1],
        21: ["Move forward 5 steps (fast but more unstable)", 1],
        22: ["Move backward 5 steps (fast but more unstable)", 1],
        23: ["Move left 5 steps (fast but more unstable)", 1],
        24: ["Move right 5 steps (fast but more unstable)", 1],
        25: ["Kick forward with left foot", 1],
        26: ["Kick forward with right foot", 1],
        27: ["*not sure* kick with left foot", 1],
        28: ["*not sure* kick with right foot", 1],
        29: ["Kick back with left foot", 1],
        30: ["Kick back with right foot", 1],
        31: ["Empty", 1],
        32: ["Defense (fighting)", 1],
        33: ["Punch forward (fighting)", 1],
        34: ["Left punch (fighting)", 1],
        35: ["Right punch (fighting)", 1],
        36: ["pose", 1],
        37: ["pose", 1],
        38: ["Empty", 1],
        39: ["cannot use", 1],
        40: ["cannot use", 1],
        41: ["cannot use", 1],
        42: ["cannot use", 1],
        43: ["cannot use", 1],
        44: ["cannot use", 1],
        45: ["cannot use", 1],
        46: ["cannot use", 1],
        47: ["cannot use", 1],
        48: ["cannot use", 1],
        49: ["cannot use", 1],
        50: ["cannot use", 1],
    }
    HUMANOID_MOTION = {
        # Condensed dictionary for all accepted movements
        # motion_num: ["name", motion_duration]
        1: HUMANOID_FULL[1],
        2: HUMANOID_FULL[2],
        3: HUMANOID_FULL[3],
        4: HUMANOID_FULL[4],
        7: HUMANOID_FULL[7],
        8: HUMANOID_FULL[8],
        9: HUMANOID_FULL[9],
        13: HUMANOID_FULL[13],
        14: HUMANOID_FULL[14],
        15: HUMANOID_FULL[15],
        16: HUMANOID_FULL[16],
        17: HUMANOID_FULL[17],
        18: HUMANOID_FULL[18],
        19: HUMANOID_FULL[19],
        20: HUMANOID_FULL[20],
        25: HUMANOID_FULL[25],
        26: HUMANOID_FULL[26],
        27: HUMANOID_FULL[27],
        28: HUMANOID_FULL[28],
        29: HUMANOID_FULL[29],
        30: HUMANOID_FULL[30],
        36: HUMANOID_FULL[36],
        37: HUMANOID_FULL[37],
    }

    SPIDER_FULL = {
        0: ["up and down", 1],
        1: ["forward slightly", 1],
        2: ["back slightly", 1],
        3: ["turn left (fast slight turn)", 1],
        4: ["turn right (fast slight turn)", 1],
        5: ["forward 6 steps (slow)", 4],
        6: ["back 6 steps (slow)", 4],
        7: ["turn left (slow mid turn)", 2],
        8: ["turn right (slow mid turn)", 2],
        9: ["slow prance", 4],
        # Dance 1: up on hind-legs and wave; forward slightly; back slightly;
        #          wiggle; up on hind-legs move front legs up and down
        10: ["dance 1", 1],
        # up and down several times; fast prance; wiggle
        11: ["dance 2", 1],
        12: ["turn right (slow big turn)", 1],
        13: ["turn left (slow big turn)", 1],
        14: ["forward then back (fast)", 1],
        15: ["dance (wiggle then remain mid height)", 1],
        16: ["slow wiggle", 1],
        17: ["stand mid height", 1],
        18: ["forward 3 steps (slow remain mid height)", 1],
        19: ["back 3 steps (slow remain mid height)", 1],
        20: ["forward continuously", 1],
        21: ["turn right continuously", 1],
        22: ["turn left continuously", 1],
        23: ["forward continuously", 1],
        29: ["wave back right paw continuous", 1],
        39: ["Stance (the legs up)", 10]
    }

    # Hex Constants  #########################################################
    HEX_STOP = b"\x09\x00\x02\x00\x00\x00\x10\x83\x9e"
    HEX_RESET = (
        b"\x11\x00\x02\x02\x00\x00\x4b\x04"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x64"
    )
    HEX_RESUME = b"\x09\x00\x02\x00\x00\x00\x13\x83\xa1"

    HEX_ACK_COMMAND = b"\x04\x00\x06\n"
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
    CV_WINDOW_ROBOT = "Robot instructions window"
    CV_FONT = cv2.FONT_HERSHEY_PLAIN
    CV_FONT_SCALE = 1
    CV_TEXT_COLOR = (255, 0, 255)
    CV_LINE_COLOR = (255, 75, 5)
    CV_LINE_COLOR2 = (5, 75, 255)
    CV_THICKNESS = 1
    CV_LINE = cv2.LINE_AA
    CV_SIZE = (128, 512, 3)
    CV_NOTE_HEIGHT = 200

    CASCADE_ROOT = PATH_ROOT + "cascade_files/"
    CV_CASCADE_FILE = (
            CASCADE_ROOT + "tennis_ball_20x20_stage14_3500samples.xml"
    )
    CV_CASCADE_FILE = CASCADE_ROOT + "haarcascade_frontalface_alt.xml"
    CV_DETECTOR = cv2.CascadeClassifier(CV_CASCADE_FILE)

    ##########################################################################
    # Camera settings   ######################################################
    ##########################################################################
    VIDEO_ROOT = PATH_ROOT + "videos/"
    PIC_ROOT = PATH_ROOT + "pictures/"
    if not os.path.exists(VIDEO_ROOT):
        os.mkdir(VIDEO_ROOT)
    if not os.path.exists(PIC_ROOT):
        os.mkdir(PIC_ROOT)
    files = os.listdir(VIDEO_ROOT)

    if len(files) > 0:
        files = [int(f[:-4]) for f in files]
        files.sort()
        vid_num = files[-1] + 1
    else:
        vid_num = 0
    CV_VIDEO_FILE = VIDEO_ROOT + f"{vid_num}.avi"

    CAM_SETTINGS_FILE = PATH_ROOT + "cam_settings.json"
    if not os.path.isfile(CAM_SETTINGS_FILE):
        with open(CAM_SETTINGS_FILE, 'w') as file:
            file.write("{}")
    else:
        with open(CAM_SETTINGS_FILE) as file:
            if file.read() == "":
                empty = True
            else:
                empty = False
        if empty:
            with open(CAM_SETTINGS_FILE, "w") as file:
                file.write("{}")

    # CS = camera settings
    CS_DEFAULT = "default"
    CS_DEFAULT1 = "default_non_pi_cam"
    CS_IS_PI_CAM = "is_pi_cam"
    CS_FOCAL = "focal_len"
    CS_LENS_TYPE = "lens_type"
    CS_OBJ_WIDTH = "object_width"
    CS_SCALE = "scale"
    CS_NEIGH = "nearest_neighbour"
    CS_X_OFFSET = 10
    CS_Y_OFFSET = 20

    CS_MID_TOLERANCE = 20
    FREQUENCY_PIC = 30
    LOOP_DUR_THRESHOLD = 200  # milliseconds before triggering a warning

    # Cam memory settings  ###################################################
    MEM_DIST_LIST_LEN = 1
    # Maximum change in distance that won't be considered an outlier
    DIST_DISCREPANCY = 20
    MAX_LAST_SEEN = 2
    KICK_DIST = 7
    KICK_RANGE = 3

    ##########################################################################
    # GUI settings  ##########################################################
    ##########################################################################
    G_FRAME_HEIGHT = 491
    G_FRAME_WIDTH = 441
    G_SLIDE_HEIGHT = 70

    ##########################################################################
    # Socket server settings  ################################################
    ##########################################################################
    LOCAL_IP = "127.0.0.1"
    PING_MONITOR_IP = "127.0.0.1"
    PING_MONITOR_PORT = 1234
    PRE_HEADER_LEN = 3
    HEADER_LEN = 10
    ENCODING = "utf-8"

    NUM_SEGMENTS = 0
    COM_IMG = 10
    COM_IMG_REQUEST = 11
    COM_TEST = 100
    COM_TEST2 = 12

    ##########################################################################
    # Log settings  ##########################################################
    ##########################################################################
    default_log_level_file = logging.DEBUG
    default_log_level_terminal = logging.DEBUG  #logging.INFO
    LOG_ROOT = PATH_ROOT + "logs/"
    if not os.path.exists(LOG_ROOT):
        os.mkdir(LOG_ROOT)
    # Main log settings  #####################################################
    LOG_MAIN_NAME = "main"
    LOG_MAIN_FILE = LOG_ROOT + LOG_MAIN_NAME + ".log"
    LOG_MAIN_FILE_LEVEL = default_log_level_file
    LOG_MAIN_STREAM_LEVEL = default_log_level_terminal
    # Camera log settings  ###################################################
    LOG_CAM_NAME = "cam"
    LOG_CAM_FILE = LOG_ROOT + LOG_CAM_NAME + ".log"
    LOG_CAM_FILE_LEVEL = default_log_level_file
    LOG_CAM_STREAM_LEVEL = default_log_level_terminal
    # Robot log settings  ####################################################
    LOG_ROBOT_NAME = "robot"
    LOG_ROBOT_FILE = LOG_ROOT + LOG_ROBOT_NAME + ".log"
    LOG_ROBOT_FILE_LEVEL = default_log_level_file
    LOG_ROBOT_STREAM_LEVEL = default_log_level_terminal
    # Robot log settings  ####################################################
    LOG_SOCKET_NAME = "socket"
    LOG_SOCKET_FILE = LOG_ROOT + LOG_SOCKET_NAME + ".log"
    LOG_SOCKET_FILE_LEVEL = default_log_level_file
    LOG_SOCKET_STREAM_LEVEL = default_log_level_terminal
    # Robot log settings  ####################################################
    LOG_GUI_NAME = "gui"
    LOG_GUI_FILE = LOG_ROOT + LOG_GUI_NAME + ".log"
    LOG_GUI_FILE_LEVEL = default_log_level_file
    LOG_GUI_STREAM_LEVEL = default_log_level_terminal

    # Misc ###################################################################
    FORMAT = "%(asctime)s: %(levelname)s: %(message)s"
    FORMAT_TERMINAL = "%(asctime)s: %(name)s: %(levelname)s: %(message)s"
    FORMAT_DATE = "%Y-%m-%d %H:%M:%S"
    MAX_BYTES = 5120
    BACKUP_COUNT = 4

    LAST_LOG = 0
    FREQUENCY_LOG = 1
    DEFAULT_LOG_FREQUENCY = 30  # seconds

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    # Log Types  #############################################################
    LOG_ROBOT_AUTO_FAIL = "robot auto gen"
    LOG_ROBOT_AUTO_FAIL_HEAD = "robot auto head"

    LOG_CAM_NUM_OBJECTS = "num objects"
    LOG_CAM_OBJECTS_NOT_FOUND = "not found"
    LOG_CAM_STOP_SEARCH = "robot has stopped searching"
    LOG_CAM_LOOP_TIME = "Total runtime"
    LOG_CAM_RECOGNITION_TIME = "Recognition loop time"
    # LOG_CAM_DEVIATION = "deviation"

    ##########################################################################
    # Locks  #################################################################
    ##########################################################################
    LOCK_CLASS = threading.Lock()
    LOCK_GEN = threading.Lock()
    LOCK_CAM = threading.Lock()
    LOCK_HUMANOID = threading.Lock()
    LOCK_SPIDER = threading.Lock()

    ##########################################################################
    # Control commands  ######################################################
    ##########################################################################
    # Terminal typed commands
    CMD_FULL_CONTROL = "full"
    CMD_EXIT = "exit"
    CMD_EXIT1 = "e"
    CMD_STOP = "stop"
    CMD_STOP1 = "s"
    CMD_DICTIONARY = "dict"
    CMD_AUTO_ON = "auto"
    CMD_AUTO_OFF = "auto off"
    CMD_FORWARD = "forward"
    CMD_FORWARD1 = "f"
    CMD_BACKWARD = "back"
    CMD_BACKWARD1 = "b"
    CMD_LEFT = "left"
    CMD_LEFT1 = "l"
    CMD_RIGHT = "right"
    CMD_RIGHT1 = "r"
    CMD_KICK = "kick"
    CMD_KICK1 = "k"
    CMD_DANCE = "dance"
    CMD_DANCE1 = "d"
    CMD_RH_UP = "head_up"
    CMD_RH_UP1 = "h_u"
    CMD_RH_DOWN = "head_down"
    CMD_RH_DOWN1 = "h_d"
    CMD_RH_LEFT = "head_left"
    CMD_RH_LEFT1 = "h_l"
    CMD_RH_RIGHT = "head_right"
    CMD_RH_RIGHT1 = "h_r"
    CMD_SET_HEAD_DELTA = "delta"
    CMD_SET_HEAD_UD = "set_ud"
    CMD_SET_HEAD_LR = "set_lr"
    CMD_VARS = "dump"
    CMD_VARS1 = "dump1"
    CMD_VARS2 = "dump2"

    # OpenCV window commands
    CMD_CV_EXIT = ord("e")
    CMD_CV_EXIT1 = ord("E")
    CMD_CV_STOP = ord("s")
    CMD_CV_STOP1 = ord("S")
    CMD_CV_DANCE = ord("d")
    CMD_CV_KICK = ord("k")
    CMD_CV_FORWARD = ord("f")
    CMD_CV_BACKWARD = ord("b")
    CMD_CV_LEFT = ord("l")
    CMD_CV_RIGHT = ord("r")
    CMD_CV_HEAD_UP = ord("U")
    CMD_CV_HEAD_DOWN = ord("D")
    CMD_CV_HEAD_LEFT = ord("L")
    CMD_CV_HEAD_RIGHT = ord("R")
    CMD_CV_HEAD_DELTA_P = ord("+")
    CMD_CV_HEAD_DELTA_M = ord("-")
    CMD_CV_DUMP_CAM = ord("1")
    CMD_CV_DUMP_ROBOT = ord("2")
    CMD_CV_DUMP_CMD = ord("3")
    ##########################################################################
    # Misc Constants
    CONST_MIDDLE = "Middle"

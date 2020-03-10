"""
Kuwin Wyke
Midwestern State University

This module contains the primary configurations for this project
"""
import cv2
import logging
from string import Template


class Conf:
    """Generic config settings"""
    CASCADE_FILE = "cascade_files/tennis_ball_20x20_stage14_3500samples.xml"
    BALL_DETECTOR = cv2.CascadeClassifier(CASCADE_FILE)
    DETECTION_SCALE = 1.1
    DETECTION_NEIGH = 10
    HAAR_VIDEO_FILE = "haar_output.avi"
    TF_VIDEO_FILE = "tf_output.avi"


class Display:
    """Constants for OpenCV window output"""
    WINDOW_HAAR = "Haar Window"
    WINDOW_TF = "TensorFlow Window"
    FONT = cv2.FONT_HERSHEY_PLAIN
    SCALE = 1.4
    TEXT_START_X = 10
    TEXT_START_Y = 50
    MAX_DISP_AREA_H = 400
    COLOR0 = (78, 255, 78)
    COLOR1 = (3, 78, 255)
    COLOR2 = (3, 78, 255)


class Log:
    """Control log settings"""
    ROOT = "logs/"
    MAIN = ROOT + "main.log"
    HAAR = ROOT + "haar.log"
    TF = ROOT + "tensorflow.log"
    MAIN_NAME = "main"
    HAAR_NAME = "haar"
    TF_NAME = "tensorflow"
    BASE_LEVEL = logging.INFO
    HAAR_LEVEL = logging.INFO
    TF_LEVEL = logging.INFO
    FORMAT = "%(asctime)s: %(levelname)s: %(message)s"
    INTERVAL = 10


class Templates:
    """Template messages for output to the user"""
    # Log messages
    FASTEST_DETECTION = Template("The fastest detection was done by $fastest")
    TIME_TAKEN = Template(
        "Time from start: $time\n"
        "Total loop time: $tot\n"
        "Haar Left: $haar_l\n"
        "Haar Right: $haar_r\n"
        "TensorFlow Left: $tf_l\n"
        "TensorFlow Right: $tf_r"
    )
    HAAR_TIME_TAKEN = Template(
        "Time from start: $time\n"
        "Haar Left: $haar_l\n"
        "Haar Right: $haar_r"
    )
    TF_TIME_TAKEN = Template(
        "Time from start: $time\n"
        "TensorFlow Left: $tf_l\n"
        "TensorFlow Right: $tf_r"
    )
    BALLS_DETECTED = Template(
        "Time since start: $time\n"
        "Balls detected (both algorithms): $balls\n"
        "Number of balls Detected by haar: $haar_balls\n"
        "Number of balls Detected by TensorFlow: $tf_balls "
    )
    HAAR_BALLS_DETECTED = Template(
        "Time since start: $time\n"
        "Balls detected (both algorithms): $balls\n"
        "Number of balls Detected by haar: $haar_balls"
    )
    TF_BALLS_DETECTED = Template(
        "Time since start: $time\n"
        "Balls detected (both algorithms): $balls\n"
        "Number of balls Detected by TensorFlow: $tf_balls "
    )

    # OpenCV window
    TIME_FROM_START = Template("Total duration: $time")
    TOT_TIME = Template("Total time for loop: $time")
    LEFT_TIME = Template("Left time: $time")
    RIGHT_TIME = Template("Right time: $time")
    TOT_BALLS_DETECTED = Template("Balls detected: $num_balls")
    LEFT_BALLS_DETECTED = Template("Left balls detected: $num_balls")
    RIGHT_BALLS_DETECTED = Template("Right balls detected: $num_balls")


class Conditionals:
    """Set special cases on or off"""
    RECORD = True

"""Kuwin Wyke
Midwestern State University
Start: 6 November 2019
End: work in progress

This module is designed to be used in the ball recognition program in the
folder named "ball_recognition_v1". It contains a class to connect to the
camera on either a raspberry pi or windows computer.
"""

from picamera.array import PiRGBArray
from picamera import PiCamera

# Project specific modules
from config import Conf
from constants import Locks
from debug import Debug


# Create class to handle camera object
class Camera:
    """ This class is used to create a camera object. With this class
    both windows and raspberry pi will be able to use the same object because
    this class will handle the differences between the two operating systems.
    """
    _inst = None

    @staticmethod
    def get_inst():
        if Camera._inst is None:
            Camera._inst = Camera()
        return Camera._inst

    # Initialize the class. No variables are required because the only
    # condition is the operating system.
    def __init__(self):
        if Debug.cam:
            print("starting camera")
        self._cam = PiCamera()
        self._cam.resolution = (Conf.SET_WIDTH, Conf.SET_HEIGHT)
        self._raw_capture = PiRGBArray(self._cam)
        self._frame = None
        self.get_frame()

    def get_frame(self):
        """ This function gets the current image in front of the camera"""
        # with Locks.CAM_LOCK:
        self._cam.capture(self._raw_capture, "bgr", True)
        self._frame = self._raw_capture.array
        self._raw_capture.truncate(0)
        return self._frame

    # Create the destructor to close the camera connections.
    def __del__(self):
        self._cam.close()

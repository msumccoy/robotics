""" Kuwin Wyke
Midwestern State University
Start: 23 December 2019
End: work in progress

***Description to be made***
"""

import platform
import cv2

# Project specific modules
import variables
from debug import debug_cam
from constants import CamConst
# Check if running on rasp pi to import pi cam modules
if platform.system() != "Windows":
    import serial
    from picamera.array import PiRGBArray
    from picamera import PiCamera


# Create class to handle camera object
class Camera:
    """ This class is used to create a camera object. With this class
    both windows and raspberry pi will be able to use the same object because
    this class will handle the differences between the two operating systems.
    """

    # Initialize the class. No variables are required because the only
    # condition is the operating system.
    def __init__(self):
        # Check if the operating system is linux, (raspberry pi will return
        # ("Linux"). The raspberry pi uses a pi cam and therefore needs
        # the pi cam implementation of the camera.
        if platform.system() == "Linux":
            if debug_cam:
                print("starting camera")
            self.cam = PiCamera()
            self.cam.resolution = (variables.set_width, variables.set_height)
            self.raw_capture = PiRGBArray(self.cam)
        else:
            if debug_cam:
                print("starting camera")
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, CamConst.WIDTH)
            self.cap.set(4, CamConst.HEIGHT)
        self.get_frame()
        # Get the actual width and height that was set.
        self.height, self.width, self.channels = self.frame.shape

    def get_frame(self):
        """ This function gets the current image in front of the camera"""
        if platform.system() == "Linux":
            self.cam.capture(self.raw_capture, "bgr", True)
            self.frame = self.raw_capture.array
            self.raw_capture.truncate(0)
        else:
            _, self.frame = self.cap.read()

    # Create the destructor to close the camera connections.
    def __del__(self):
        if platform.system() == "Linux":
            self.cam.close()
        else:
            self.cap.release()

""" Kuwin Wyke
Midwestern State University
Start: 27 October 2019
End: Work in Progress

This program is to test and demonstrate object oriented programing
constructs in python. As well as python decorators.

Currently this program starts a camera as an object. This is to practice
creating a camera object with its own methods to hand multiple operating
systems and different camera operation on each.
"""

import cv2
import platform
# Only import picamera modules if using raspberry pi
if platform.system() == "Linux":
    from picamera.array import PiRGBArray
    from picamera import PiCamera


class Camera:
    """ This class is used to create a camera object. With this class
    both windows and raspberry pi will be able to use the same object
    which will handle the differences between the two operating systems.
    """
    # Set a default height and width (if the dimensions are off the programing
    # language will correct it automatically I think.
    set_width = 320
    set_height = 240

    # Initialize the class. No variables are required because the only
    # condition is the operating system.
    def __init__(self):
        # Check if the operating system is linux as this is what the raspberry
        # pi will return. The raspberry pi uses a pi cam and therefore needs
        # the pi cam implementation of the camera.
        if platform.system() == "Linux":
            print("starting camera")
            self.cam = PiCamera()
            self.cam.resolution = (self.set_width, self.set_height)
            self.raw_capture = PiRGBArray(self.cam)
        else:
            print("starting camera")
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, self.set_width)
            self.cap.set(4, self.set_height)
        self.get_frame()
        # Get the actual width and height that was set.
        self.height, self.set_width, self.channels = self.frame.shape

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


def main():
    # Create camera object
    camera = Camera()
    cv2.imshow("test", camera.frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

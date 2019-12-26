""" Kuwin Wyke
Midwestern State University
Start: 23 December 2019
End: work in progress

***Description to be made***
"""

import cv2

import exit_control
from camera import Camera
from variables import General


def photo_loop():
    cam = Camera()
    while not General.exit_code:
        cam.get_frame()
        cv2.imshow("frame", cam.frame)
        exit_var = cv2.waitKey(1000)
        exit_control.trigger_exit(exit_var, cam.frame)
    cv2.destroyAllWindows()
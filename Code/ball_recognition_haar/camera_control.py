"""
Kuwin Wyke
Midwestern State University

This module is used to handle camera controls
"""
import cv2
import logging

from ball_recognition_haar.config import Log, Templates
from ball_recognition_haar.enums import LensType


class CameraControl:
    _inst = None
    logger = logging.getLogger(Log.NAME)

    def __init__(self, lens_type):
        # Start camera and get frame
        self.cam = cv2.VideoCapture(0)
        self.type = lens_type
        _, self.frame = self.cam.read()
        height, width, _ = self.frame.shape
        mid_point = int(width / 2)
        self.frame_left = self.frame[0: height, 0: mid_point]
        self.frame_right = self.frame[0: height, mid_point: width]
        height, width, _ = self.frame_right.shape
        if height > width:
            self.logger.warning(Templates.WARN_CAM_TYPE.substitute())

    @staticmethod
    def get_inst(lens_type):
        if CameraControl._inst is None:
            CameraControl._inst = CameraControl(lens_type)
        return CameraControl._inst

    def get_next_frame(self):
        _, self.frame = self.cam.read()
        height, width, _ = self.frame.shape
        mid_point = int(width / 2)
        self.frame_left = self.frame[0: height, 0: mid_point]
        self.frame_right = self.frame[0: height, mid_point: width]




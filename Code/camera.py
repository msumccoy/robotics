"""
Kuwin Wyke
Midwestern State University
"""
import logging
import time

import cv2

from config import Conf
from enums import RobotType, LensType
from variables import ExitControl


class Camera:
    _inst = {}
    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)

    @staticmethod
    def get_inst(cam_name, cam_num=0, lens_type=LensType.SINGLE, record=True):
        if cam_name not in Camera._inst:
            Camera._inst[cam_name] = Camera(cam_num, lens_type, record)
        return Camera._inst[cam_name]

    def __init__(self, cam_num, lens_type, record):
        self.start = time.time()
        self.cam = cv2.VideoCapture(cam_num)
        self.ret, self.frame = self.cam.read()
        self.height, self.width, _ = self.frame.shape

        self.frame_left = None
        self.frame_right = None
        self.lens_type = lens_type
        if lens_type == LensType.DOUBLE:
            self.get_dual_image()
            if self.height > self.width:
                self.main_logger.warning(Conf.WARN_CAM_TYPE.substitute())

        self.record = record
        if record:
            width = self.width
            height = self.height
            self.video_writer = cv2.VideoWriter(
                Conf.CV_VIDEO_FILE,
                cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                10, (width, height)
            )

    def get_dual_image(self):
        mid_point = int(self.width / 2)
        self.frame_left = self.frame[0: self.height, 0: mid_point]
        self.frame_right = self.frame[0: self.height, mid_point: self.width]

    def start_recognition(self):
        while not ExitControl.gen:
            self.ret, self.frame = self.cam.read()
            if self.lens_type == LensType.DOUBLE:
                self.get_dual_image()

            cv2.imshow(Conf.CV_IMG_WINDOW, self.frame)
            if self.record:
                self.video_writer.write(self.frame)
            k = cv2.waitKey(1)
            if k == 27:
                ExitControl.gen = True


if __name__ == "__main__":
    cam = Camera.get_inst(RobotType.SPIDER)
    cam.start_recognition()

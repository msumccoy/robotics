"""
Kuwin Wyke
Midwestern State University
"""
import logging
import time
import cv2

import log_set_up
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

        self.is_detected = False
        self.scale = 10
        self.neigh = 4
        track_bar = Conf.CV_IMG_WINDOW
        cv2.namedWindow(Conf.CV_IMG_WINDOW)
        cv2.namedWindow(track_bar)
        cv2.createTrackbar(
            "scale", track_bar, 4, 89, self.set_scale
        )
        cv2.createTrackbar(
            "min Neigh", track_bar, 4, 50, self.set_neigh
        )

    def start_recognition(self):
        while not ExitControl.gen:
            self.ret, self.frame = self.cam.read()
            if self.lens_type == LensType.DOUBLE:
                self.get_dual_image()
            self.detect()
            cv2.imshow(Conf.CV_IMG_WINDOW, self.frame)
            if self.record:
                self.video_writer.write(self.frame)
            k = cv2.waitKey(1)
            if k == 27:
                ExitControl.gen = True

    def detect(self):
        if self.lens_type == LensType.SINGLE:
            gray_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            balls = Conf.CV_DETECTOR.detectMultiScale(
                gray_frame, self.scale, self.neigh
            )
            for (x, y, w, h) in balls:
                x1 = x + w
                y1 = y + h
                cv2.rectangle(
                    self.frame, (x, y), (x1, y1), Conf.CV_LINE_COLOR
                )
            self.main_logger.info(balls)

    def get_dual_image(self):
        mid_point = int(self.width / 2)
        self.frame_left = self.frame[0: self.height, 0: mid_point]
        self.frame_right = self.frame[0: self.height, mid_point: self.width]

    def set_scale(self, position):
        self.scale = 0.1 * position + 1.005

    def set_neigh(self, position):
        self.neigh = position


if __name__ == "__main__":
    cam = Camera.get_inst(RobotType.SPIDER, record=False)
    cam.start_recognition()

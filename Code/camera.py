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
        if lens_type != LensType.SINGLE and lens_type != LensType.DOUBLE:
            raise ValueError(f"'{lens_type}' is not a valid lens type")
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

        self.num_objects = 0
        self.num_left = 0
        self.num_right = 0
        self.detected_objects = None
        self.detected_left = None
        self.detected_right = None
        self.is_detected_equal = True
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
            self.draw_bounding_box()
            cv2.imshow(Conf.CV_IMG_WINDOW, self.frame)
            if self.record:
                self.video_writer.write(self.frame)
            k = cv2.waitKey(1)
            if k == 27:
                ExitControl.gen = True

    def detect(self):
        if self.lens_type == LensType.SINGLE:
            gray_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            self.detected_objects = Conf.CV_DETECTOR.detectMultiScale(
                gray_frame, self.scale, self.neigh
            )
        elif self.lens_type == LensType.DOUBLE:
            gray_left = cv2.cvtColor(self.frame_left, cv2.COLOR_BGR2GRAY)
            gray_right = cv2.cvtColor(self.frame_right, cv2.COLOR_BGR2GRAY)
            self.detected_left = Conf.CV_DETECTOR.detectMultiScale(
                gray_left, self.scale, self.neigh
            )
            self.detected_right = Conf.CV_DETECTOR.detectMultiScale(
                gray_right, self.scale, self.neigh
            )

    def draw_bounding_box(self):
        if self.lens_type == LensType.SINGLE:
            self.num_objects = len(self.detected_objects)
            for (x, y, w, h) in self.detected_objects:
                x1 = x + w
                y1 = y + h
                cv2.rectangle(
                    self.frame, (x, y), (x1, y1), Conf.CV_LINE_COLOR
                )
        elif self.lens_type == LensType.DOUBLE:
            self.num_left = len(self.detected_left)
            self.num_right = len(self.detected_right)
            if self.num_left == self.num_right:
                self.is_detected_equal = True
            else:
                self.is_detected_equal = False
            for (x, y, w, h) in self.detected_left:
                x1 = x + w
                y1 = y + h
                cv2.rectangle(
                    self.frame, (x, y), (x1, y1), Conf.CV_LINE_COLOR
                )
            for (x, y, w, h) in self.detected_right:
                x1 = x + w + self.midpoint
                y1 = y + h
                cv2.rectangle(
                    self.frame, (x, y), (x1, y1), Conf.CV_LINE_COLOR
                )

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

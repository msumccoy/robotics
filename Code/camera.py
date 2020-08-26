"""
Kuwin Wyke
Midwestern State University
"""
import logging
import time
import cv2

import log_set_up
from config import Conf
from enums import RobotType, LensType, DistanceType
from variables import ExitControl


class Camera:
    _inst = {}
    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)

    @staticmethod
    def get_inst(
            cam_name, cam_num=0, lens_type=LensType.SINGLE,
            record=True, focal_len=None
    ):
        if cam_name not in Camera._inst:
            Camera._inst[cam_name] = Camera(
                cam_num, lens_type, record, focal_len
            )
        return Camera._inst[cam_name]

    def __init__(self, cam_num, lens_type, record, focal_len=None):
        self.count = 0
        if lens_type != LensType.SINGLE and lens_type != LensType.DOUBLE:
            raise ValueError(f"'{lens_type}' is not a valid lens type")
        self.start = time.time()
        self.cam = cv2.VideoCapture(cam_num)
        self.ret, self.frame = self.cam.read()
        self.height, self.width, _ = self.frame.shape

        if focal_len is None:
            self.focal_len = Conf.CAM_FOCAL_LEN
        else:
            self.focal_len = focal_len

        self.frame_left = None
        self.frame_right = None
        self.midpoint = None
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

        self.objects = {}
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
        track_bar = Conf.CV_WINDOW
        cv2.namedWindow(Conf.CV_WINDOW)
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
            self.detect_object()
            cv2.imshow(Conf.CV_WINDOW, self.frame)
            if self.lens_type == LensType.DOUBLE:
                cv2.imshow(Conf.CV_WINDOW_LEFT, self.frame_left)
                cv2.imshow(Conf.CV_WINDOW_RIGHT, self.frame_right)
            if self.record:
                self.video_writer.write(self.frame)
            k = cv2.waitKey(1)
            if k == 27:
                ExitControl.gen = True

    def detect_object(self):
        if self.lens_type == LensType.SINGLE:
            gray_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            self.detected_objects = Conf.CV_DETECTOR.detectMultiScale(
                gray_frame, self.scale, self.neigh
            )
            if self.detected_objects is not None:
                self.num_objects = len(self.detected_objects)
            else:
                self.num_objects = 0
        elif self.lens_type == LensType.DOUBLE:
            gray_left = cv2.cvtColor(self.frame_left, cv2.COLOR_BGR2GRAY)
            gray_right = cv2.cvtColor(self.frame_right, cv2.COLOR_BGR2GRAY)
            self.detected_left = Conf.CV_DETECTOR.detectMultiScale(
                gray_left, self.scale, self.neigh
            )
            self.detected_right = Conf.CV_DETECTOR.detectMultiScale(
                gray_right, self.scale, self.neigh
            )
            self.num_left = len(self.detected_left)
            self.num_right = len(self.detected_right)
            self.num_objects = self.num_left
            if self.num_left == self.num_right:
                self.is_detected_equal = True
            else:
                self.is_detected_equal = False
                if self.num_right > self.num_left:
                    self.num_objects = self.num_right


        ######################################################################
        # Draw bounding boxes and record distances ect.  #####################
        ######################################################################
        # Formula: F = (P x  D) / W
        # Transposed: D = (F x W) / P
        # F is focal length, P is pixel width, D is distance, W is width irl
        self.objects = {}
        index = 0
        if self.lens_type == LensType.SINGLE:
            for (x, y, w, h) in self.detected_objects:
                self.objects[index] = {}
                self.objects[index][DistanceType.MAIN] = (
                    (self.focal_len * Conf.OBJ_WIDTH) / w
                )
                index += 1
                x1 = x + w
                y1 = y + h
                cv2.rectangle(
                    self.frame, (x, y), (x1, y1), Conf.CV_LINE_COLOR
                )
        elif self.lens_type == LensType.DOUBLE:
            if (
                    self.is_detected_equal
                    or self.num_left <= 1 and self.num_right <= 1
            ):
                for i in range(self.num_objects):
                    self.objects[i] = {}
                for (x, y, w, h) in self.detected_left:
                    self.objects[index][DistanceType.LEFT] = (
                        (self.focal_len * Conf.OBJ_WIDTH) / w
                    )
                    index += 1
                    x1 = x + w
                    y1 = y + h
                    cv2.rectangle(
                        self.frame_left, (x, y), (x1, y1), Conf.CV_LINE_COLOR
                    )
                index = 0
                for (x, y, w, h) in self.detected_right:
                    self.objects[index][DistanceType.RIGHT] = (
                        (self.focal_len * Conf.OBJ_WIDTH) / w
                    )
                    index += 1
                    x1 = x + w
                    y1 = y + h
                    cv2.rectangle(
                        self.frame_right, (x, y), (x1, y1), Conf.CV_LINE_COLOR
                    )
                for i in range(self.num_objects):
                    if (
                            DistanceType.LEFT in self.objects[i]
                            and DistanceType.RIGHT in self.objects[i]
                    ):
                        self.objects[i][DistanceType.MAIN] = (
                            (
                                self.objects[i][DistanceType.LEFT]
                                + self.objects[i][DistanceType.RIGHT]
                            ) / 2
                        )
                print(self.objects)
            else:
                # handle how to do each object detected in each side
                pass

    def get_dual_image(self):
        self.midpoint = int(self.width / 2)
        self.frame_left = self.frame[0: self.height, 0: self.midpoint]
        self.frame_right = (
            self.frame[0: self.height, self.midpoint: self.width]
        )

    def set_scale(self, position):
        self.scale = 0.1 * position + 1.005

    def set_neigh(self, position):
        self.neigh = position


def main():
    cam = Camera.get_inst(
        RobotType.SPIDER, record=False, cam_num=0, lens_type=LensType.SINGLE
    )
    cam.start_recognition()


if __name__ == "__main__":
    main()

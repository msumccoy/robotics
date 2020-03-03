"""
Kuwin Wyke

"""
import cv2
import logging

from ball_recognition_haar.custom_wraps import time_wrapper
from ball_recognition_haar.config import Conf, Log


logger = logging.getLogger(Log.NAME)


class Calibrator:
    _inst = None

    def __init__(self):
        starting_scale = 1
        starting_neigh = 4
        track_bar = Conf.BALL_WINDOW_MAIN
        cv2.namedWindow(Conf.BALL_WINDOW_MAIN)
        cv2.namedWindow(track_bar)
        cv2.createTrackbar(
            "scale", track_bar, starting_scale, 89, self.set_scale
        )
        cv2.createTrackbar(
            "min Neigh", track_bar, starting_neigh, 50, self.set_neigh
        )
        self.scale = None
        self.set_scale(starting_scale)
        self.neigh = None
        self.set_neigh(starting_neigh)

    @staticmethod
    def get_inst():
        if Calibrator._inst is None:
            Calibrator._inst = Calibrator()
        return Calibrator._inst

    def set_scale(self, position):
        self.scale = 0.1 * position + 1.005
        print(self.scale)

    def set_neigh(self, position):
        self.neigh = position
        print(self.neigh)


@time_wrapper
def dual_detect(frame1, frame2, frame1_name, frame2_name):
    xy1 = detect_ball(frame1, name=frame1_name)
    xy2 = detect_ball(frame2, name=frame2_name)
    return xy1, xy2


@time_wrapper
def detect_ball(frame):
    calibrator = Calibrator.get_inst()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    balls = Conf.BALL_DETECTOR.detectMultiScale(
        gray_frame, calibrator.scale, calibrator.neigh
    )
    xy = []
    for (x, y, w, h) in balls:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 75, 5))
        xy.append((x, y))

    return xy

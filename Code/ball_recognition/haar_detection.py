"""
Kuwin Wyke
Midwestern State University

This module is used to execute haar detection
"""
import time
import cv2

from config import Conf, Display


def haar_detection(img):
    start = time.time()
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    balls = Conf.BALL_DETECTOR.detectMultiScale(
        gray_img,
        Conf.DETECTION_SCALE,
        Conf.DETECTION_NEIGH
    )
    detect_time = time.time() - start

    points = []
    for (x, y, w, h) in balls:
        cv2.rectangle(img, (x, y), (x + w, y + h), Display.COLOR0)
        points.append((x, y))

    return detect_time, points

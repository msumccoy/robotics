"""
Kuwin Wyke
Midwestern State University

This program is designed for use with a dual lens camera that outputs a
single image with the two views presented horizontally. The object of this
program is to measure the time taken to detect a tennis ball using a haar
cascade. This information is to be stored in a log file.
"""
import cv2
import logging
import time

from ball_recognition_haar import log_set_up
from ball_recognition_haar.config import Conf, Log, Templates
from ball_recognition_haar.detection import dual_detect


def main():
    logger = logging.getLogger(Log.NAME)
    # Start Camera
    cam = cv2.VideoCapture(0)
    end = False
    while not end:
        # Get camera frame and separate left and right images
        _, frame = cam.read()
        height, width, _ = frame.shape
        mid_point = int(width / 2)
        frame_left = frame[0: height, 0: mid_point]
        frame_right = frame[0: height, mid_point: width]
        height, width, _ = frame_right.shape
        if height > width:
            logger.warning(Templates.WARN_CAM_TYPE.substitute())

        # Detect ball in both images and time execution
        xy_left, xy_right = dual_detect(
            frame_left, frame_right, frame1_name="Left Frame",
            frame2_name="Right Frame"
        )
        if len(xy_left) == len(xy_right):
            for xy1, xy2 in zip(xy_left, xy_right):
                print("xy_left: {} -- xy_right: {}".format(xy1, xy2))
        cv2.imshow(Conf.BALL_WINDOW_MAIN, frame)
        cv2.imshow(Conf.BALL_WINDOW_LEFT, frame_left)
        cv2.imshow(Conf.BALL_WINDOW_RIGHT, frame_right)
        k = cv2.waitKey(1)
        if k == 27:  # Esc = 27
            end = True
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

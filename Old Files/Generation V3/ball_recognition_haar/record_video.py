"""
Kuwin Wyke
Midwestern State University

This module is used to record the output from the camera and save the video
with the current metrics at the bottom.
"""
import numpy as np
import cv2

from ball_recognition_haar.config import Conf


def record_video(img, img_writer, time_elapsed, num_detections):
    display_area = np.zeros_like(img)[0: Conf.DISPLAY_AREA]
    cv2.putText(
        display_area,
        f"time elapsed: {time_elapsed:.2f}",
        (10, 50),
        cv2.FONT_HERSHEY_PLAIN,
        2,
        Conf.TEXT_COLOR
    )
    cv2.putText(
        display_area,
        f"Detections: {num_detections}",
        (10, 100),
        cv2.FONT_HERSHEY_PLAIN,
        2,
        Conf.TEXT_COLOR
    )
    new_img = np.concatenate((img, display_area), axis=0)
    img_writer.write(new_img)
    print(new_img.shape)
    cv2.imshow(Conf.BALL_WINDOW_MAIN, new_img)

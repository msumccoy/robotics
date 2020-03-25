""" Kuwin Wyke
Midwestern State University

This module contains the loop used to label images. A large amount of the
processing is done inside of the ImageHandler class
"""
import cv2
import numpy as np

from image_handler import ImageHandler


def label_images():
    img_handler = ImageHandler.get_inst()
    while not img_handler.end:
        img_handler.get_new_img()
        k = cv2.waitKey(1000)
        if k == 32:  # Space bar
            img_handler.save_labels()
        elif k == 27 or k == ord("s"):
            img_handler.end = True
            img_handler.save_label_file()
        elif k == ord("x") or k == ord("X"):
            img_handler.skip()
        elif k == ord("r") or k == ord("R"):
            img_handler.restart()
        elif k == ord("d") or k == ord("D"):
            img_handler.delete_img()
        elif k == ord("b") or k == ord("B"):
            if img_handler.block_section:
                img_handler.block_section = False
            else:
                img_handler.block_section = True
    cv2.destroyAllWindows()

""" Kuwin Wyke
Midwestern State University

This module contains the loop used to label images.
"""
import cv2
import numpy as np

from config import CV_Window
from image_handler import ImageHandler
from misc import add_text_to_img


def label_images(image_location):
    img_handler = ImageHandler.get_inst(image_location)
    while not img_handler.end:
        img_handler.get_new_img()
        # Determine the number of objects in the image
        while img_handler.item_count == 0:
            blank_image = np.zeros((300, 1000, 3), np.uint8)
            add_text_to_img(CV_Window.REQUEST_MESSAGE, blank_image)
            cv2.imshow(CV_Window.REQUEST_WINDOW, blank_image)
            k = cv2.waitKey()
            if k == ord("1"):
                img_handler.item_count = 1
            elif k == ord("2"):
                img_handler.item_count = 2
            elif k == ord("3"):
                img_handler.item_count = 3
            elif k == ord("4"):
                img_handler.item_count = 4
            elif k == ord("5"):
                img_handler.item_count = 5
            elif k == ord("6"):
                img_handler.item_count = 6
            elif k == ord("7"):
                img_handler.item_count = 7
            elif k == ord("8"):
                img_handler.item_count = 8
            elif k == ord("9"):
                img_handler.item_count = 9
            elif k == 27 or k == ord("q"):
                img_handler.end = True
                img_handler.item_count = None
        cv2.destroyWindow(CV_Window.REQUEST_WINDOW)
        if img_handler.item_count is not None and img_handler.item_count > 0:
            k = cv2.waitKey(1000)
            if k == 27 or k == ord("s"):
                img_handler.end = True
            elif k == ord("x") or k == ord("X"):
                img_handler.skip()
            elif k == ord("r") or k == ord("R"):
                img_handler.restart()
    cv2.destroyAllWindows()
    img_handler.finish()
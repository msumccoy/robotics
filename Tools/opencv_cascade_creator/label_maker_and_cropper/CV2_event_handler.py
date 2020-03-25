""" Kuwin Wyke
Midwestern State University

This module contains all opencv events
"""
import cv2

import image_handler


def mouse_events(event, x, y, flags, param):
    # This function is used to initiate the drawing of the bounding box or
    # cross hairs
    if event == cv2.EVENT_LBUTTONDOWN:
        img_handler = image_handler.ImageHandler.get_inst()
        if img_handler.first_point:
            img_handler.set_top_left(x, y)
        else:
            img_handler.set_bottom_right(x, y)
    elif event == cv2.EVENT_MOUSEMOVE:
        img_handler = image_handler.ImageHandler.get_inst()
        if img_handler.first_point:
            img_handler.draw_cross(x, y)
        else:
            img_handler.update_box(x, y)

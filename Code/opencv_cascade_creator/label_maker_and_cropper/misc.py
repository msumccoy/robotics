""" Kuwin Wyke
Midwestern State University

This module contains all miscellaneous functions
"""
import cv2

from config import CV_Window


def add_text_to_img(
        first_message, img, color=CV_Window.COLOR, second_message=" "
):
    # Add two messages to the top left corner of an image
    cv2.putText(
        img, first_message, CV_Window.ORG, CV_Window.FONT,
        CV_Window.FONT_SCALE, color, CV_Window.THICKNESS
    )
    next_org = (
        CV_Window.ORG[0],
        CV_Window.ORG[1] * 3
    )
    cv2.putText(
        img, second_message, next_org, CV_Window.FONT,
        CV_Window.FONT_SCALE, color, CV_Window.THICKNESS
    )

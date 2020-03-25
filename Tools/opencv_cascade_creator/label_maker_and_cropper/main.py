"""
Kuwin Wyke
Midwestern State University

This program is used to label images for OpenCV's C++ application to train
haar cascades. If the images are larger than config.Conf.MAX_IMG_WIDTH they
will be resized. The program also has the power to used the labeled images to
crop out the object to be used with OpenCV's application to create images.

*** HOW TO USE ***
To use this program place the images you want to label in the folder
designated by config.Conf.ORIG_IMG_FOLDER. Once completed the labeled images
will be in the folder designated by config.Conf.LABELED_IMG_FOLDER.
"""
import cv2
import os
import numpy as np

from config import Conf
from image_cropper import cut_out_objects
from label_images import label_images
from image_handler import validate_labled_images


def main():
    print(f"Image labeler version number {Conf.VERSION}")

    # label_images()  # Label images in folder
    # # check if the user wants to validate the labeled images
    # response = input(
    #     "Validate labeled imaged?\n'y' for yes\n"
    # )
    # if response == 'y' or response == 'Y':
    #     validate_labled_images()

    validate_labled_images()

    # cut_out_objects()  # Cut/crop images


if __name__ == '__main__':
    main()

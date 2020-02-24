""" Kuwin Wyke
Midwestern State University

This module houses the ImageHandler class which is used to handle obtaining
new images and labeling them.

This module is incomplete but functional
"""

import cv2
import os
import time
import numpy as np

from config import Conf, CamConf, CV_Window
from CV2_events import mouse_click
from enums import IMG_LOC_TYPE
from misc import add_text_to_img


class ImageHandler:
    """
    This class controls the behaviour of the image labeling system.
    """
    _inst = [None, None]

    def __init__(self, location):
        # The type of image (from camera or from file)
        self._location = location
        # The number of camera images obtained
        self._index = 0
        self._img = None
        # A copy is used so that a pure copy of the image can be saved without
        # drawings
        self._img_copy = None
        self._img_name = None
        self._x = None
        self._y = None
        # All the coordinates for the bounding box (bb)
        self._bb_coords = []
        # Each image name and the bb coordinates
        self._coord_dict = {}
        self._next_img = True
        # Number of items in the image
        self.item_count = 0
        self.end = False
        self.first_point = True
        if self._location is IMG_LOC_TYPE.CAM:
            self._cap = cv2.VideoCapture(0)
            # self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, CamConf.WIDTH)
            # self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CamConf.HEIGHT)
            # Give camera time to warm up
            time.sleep(2)
        elif self._location is IMG_LOC_TYPE.FILE:
            self._images = [img for img in os.listdir(Conf.IMG_PATH)]
            self._num_images = len(self._images)
        if not os.path.exists(Conf.IMG_PATH):
            os.mkdir(Conf.IMG_PATH)
        cv2.namedWindow(CV_Window.WINDOW_NAME)
        cv2.setMouseCallback(CV_Window.WINDOW_NAME, mouse_click, location)

    @staticmethod
    def get_inst(location=None):
        # Allow all functions to use one instance of the classes which creates
        # locally controlled global variables.
        if location is IMG_LOC_TYPE.CAM:
            if ImageHandler._inst[0] is None:
                ImageHandler._inst[0] = ImageHandler(location)
            return ImageHandler._inst[0]
        elif location is IMG_LOC_TYPE.FILE:
            if ImageHandler._inst[1] is None:
                ImageHandler._inst[1] = ImageHandler(location)
            return ImageHandler._inst[1]
        return ImageHandler(location)

    def show_image(self):
        if self.item_count == 0:
            self.get_new_img()
        cv2.imshow(CV_Window.WINDOW_NAME, self._img_copy)

    def get_new_img(self):
        if self._next_img:
            self._next_img = False
            self.item_count = 0
            if self._location is IMG_LOC_TYPE.CAM:
                _, self._img = self._cap.read()
                self._img_name = (
                        Conf.IMG_PATH + "_cam" + str(self._index) + ".jpg"
                )
                self._index += 1
            elif self._location is IMG_LOC_TYPE.FILE:
                if self._index < self._num_images:
                    self._img = cv2.imread(
                        Conf.IMG_PATH + str(self._images[self._index])
                    )
                    self._img_name =(
                            Conf.IMG_PATH + "_file"
                            + str(self._images[self._index])
                    )
                    os.rename(
                        Conf.IMG_PATH + str(self._images[self._index]),
                        Conf.IMG_PATH + "_file"
                        + str(self._images[self._index])
                    )
                    self._index += 1
                else:
                    self.end = True
                    return
            self._img = cv2.resize(
                self._img, (CamConf.RESIZE, CamConf.RESIZE)
            )
            self._img_copy = self._img.copy()
            add_text_to_img(self._img_name, self._img_copy)
            self.show_image()

    def set_top_left(self, x, y):
        # The upper left corner of the bounding box
        self._x = x
        self._y = y
        self.first_point = False
        cv2.circle(self._img_copy, (x, y), 1, CV_Window.COLOR)

    def set_bottom_right(self, x, y):
        # Lower right corner of bounding box
        if self._validate_coords(x, y):
            self._bb_coords.append(((self._x, self._y), (x, y)))
            self.first_point = True
            # Draw the bounding box
            cv2.rectangle(
                self._img_copy,
                (self._x, self._y),
                (x, y),
                CV_Window.COLOR
            )
            # If this is the final point
            if len(self._bb_coords) == self.item_count:
                self.item_count = 0
                # Display instructions on a blank image
                blank_image = np.zeros((300, 1000, 3), np.uint8)
                add_text_to_img(CV_Window.ACCEPT_MESSAGE, blank_image)
                cv2.imshow(CV_Window.REQUEST_WINDOW, blank_image)
                self.show_image()
                k = cv2.waitKey()
                if k == 27:  # Esc
                    print("Not saving and exiting")
                    self.end = True
                elif k == ord("r") or k == ord("R"):
                    print("restarting labeling process")
                    self._img_copy = self._img.copy()
                    add_text_to_img(self._img_name, self._img_copy)
                elif k == ord("x") or k == ord("X"):
                    print("skipping")
                    self._next_img = True
                elif k != -1 and k != 255:  # -1 or 255 is default
                    # Save the image and the labels
                    if self._location is IMG_LOC_TYPE.CAM:
                        print(self._img_name)
                        cv2.imwrite(self._img_name, self._img)
                    self._coord_dict[self._img_name] = self._bb_coords
                    self._next_img = True
                    print(self._coord_dict[self._img_name])
                self._bb_coords = []
        else:
            print("Invalid coordinates, please re-enter them")
            self._img_copy = self._img.copy()
            add_text_to_img(self._img_name, self._img_copy)
            for coords in self._bb_coords:
                cv2.rectangle(
                    self._img_copy, coords[0], coords[1], CV_Window.COLOR
                )
            self.first_point = True

    def _validate_coords(self, x, y):
        # Create edge detection algorithm to ensure boxes do not overlap.
        # Incomplete
        if self._x < x and self._y < y:
            return True
        else:
            return False

    def accept_label_points(self):
        if not self._next_img and self.item_count > 0:
            return True
        else:
            return False

    def update_box(self, x, y):
        self._img_copy = self._img.copy()
        add_text_to_img(self._img_name, self._img_copy)
        cv2.rectangle(
            self._img_copy,
            (self._x, self._y),
            (x, y),
            CV_Window.COLOR
        )
        self.show_image()

    def draw_cross(self, x, y):
        self._img_copy = self._img.copy()
        add_text_to_img(self._img_name, self._img_copy)
        width, height, depth = self._img_copy.shape
        cv2.line(self._img_copy, (x, 0), (x, height), CV_Window.COLOR)
        cv2.line(self._img_copy, (0, y), (width, y), CV_Window.COLOR)
        self.show_image()

    def skip(self):
        print("skipping")
        self._next_img = True

    def restart(self):
        print("restarting labeling process")
        self._img_copy = self._img.copy()
        add_text_to_img(self._img_name, self._img_copy)

    def save_raw(self):
        # Save labeling data
        print("Writing to file")
        with open(Conf.RAW_LABEL_FILE, "a") as file:
            with open(Conf.FULL_LABEL_FILE, "a") as full_file:
                for key in self._coord_dict:
                    line = "{} {} ".format(key, len(self._coord_dict[key]))
                    for coords in self._coord_dict[key]:
                        width = coords[1][0] - coords[0][0]
                        height = coords[1][1] - coords[0][1]
                        line += "{} {} {} {} ".format(
                            coords[0][0], coords[0][1], width, height
                        )
                    line += "\n"
                    file.write(line)
                    full_file.write(line)

    def finish(self):
        # Perform post operation clean up
        self.save_raw()
        if self._location is IMG_LOC_TYPE.CAM:
            self._cap.release()
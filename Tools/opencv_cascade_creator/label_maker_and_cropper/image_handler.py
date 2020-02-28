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

from config import Conf, CV_Window
from CV2_events import mouse_click
from enums import IMG_LOC_TYPE, COORDS_P, COORDS_XY
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
        if not os.path.exists(Conf.IMG_PATH):
            os.mkdir(Conf.IMG_PATH)
        if not os.path.exists(Conf.IMG_PATH_FILE):
            raise FileNotFoundError(
                "the file with the original images was not found: {}".format(
                    Conf.IMG_PATH_FILE
                )
            )
        if self._location is IMG_LOC_TYPE.CAM:
            print("starting Camera")
            self._cap = cv2.VideoCapture(0)
            cam_pics = [
                pic for pic in os.listdir(Conf.IMG_PATH)
                if pic.startswith(Conf.CAM_PREFIX)
            ]
            pic_num = 0
            for pic in cam_pics:
                try:
                    # get index number of pic
                    pic_num = int(pic.split(".")[0][len(Conf.CAM_PREFIX):])
                except ValueError:
                    print("{} was not created by this program".format(pic))
                if pic_num > self._index:
                    self._index = pic_num
            # Give camera time to warm up
            time.sleep(.1)
        elif self._location is IMG_LOC_TYPE.FILE:
            self._images = [img for img in os.listdir(Conf.IMG_PATH_FILE)]
            self._num_images = len(self._images)
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
                good = False
                while not good:
                    _, self._img = self._cap.read()
                    cv2.imshow(CV_Window.WINDOW_NAME, self._img)
                    k = cv2.waitKey(1)
                    if k != -1 and k != 255:
                        good = True
                self._img_name = ("_cam" + str(self._index) + ".jpg")
                self._index += 1
            elif self._location is IMG_LOC_TYPE.FILE:
                if self._index < self._num_images:
                    self._img = cv2.imread(
                        Conf.IMG_PATH_FILE +
                        "/" + str(self._images[self._index])
                    )
                    self._img_name = (
                            Conf.FILE_PREFIX + str(self._images[self._index])
                    )
                    self._index += 1
                else:
                    self.end = True
                    return
            height, width, _ = self._img.shape
            print(self._img.shape)
            if width > Conf.MAX_IMG_WIDTH:
                quotient = width / Conf.MAX_IMG_WIDTH
                width = Conf.MAX_IMG_WIDTH
                height = height / quotient
                height = int(height)
                self._img = cv2.resize(self._img, (width, height))
            print(self._img.shape)
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
        # Switch the points if they were placed in wrong order
        if self._x > x:
            temp_x = self._x
            self._x = x
            x = temp_x
        if self._y > y:
            temp_y = self._y
            self._y = y
            y = temp_y
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
                add_text_to_img(
                    CV_Window.ACCEPT_MESSAGE, blank_image, CV_Window.COLOR2
                )
                cv2.imshow(CV_Window.REQUEST_WINDOW, blank_image)
                self.show_image()
                k = cv2.waitKey()
                cv2.destroyWindow(CV_Window.REQUEST_WINDOW)
                if k == 27:  # Esc
                    print("Not saving and exiting")
                    self.end = True
                elif k == ord("r") or k == ord("R"):
                    print("restarting labeling process")
                elif k == ord("x") or k == ord("X"):
                    print("skipping")
                    self._next_img = True
                elif k != -1 and k != 255:  # -1 or 255 is default
                    # Save the image and the labels
                    cv2.imwrite(
                        Conf.IMG_PATH + "/" + self._img_name, self._img
                    )
                    self._coord_dict[self._img_name] = self._bb_coords
                    self._next_img = True
                self._bb_coords = []
        else:
            print("Invalid coordinates, please re-enter them")
            self.refresh_img()
            self.first_point = True

    def refresh_img(self):
        self._img_copy = self._img.copy()
        add_text_to_img(self._img_name, self._img_copy)
        for coords in self._bb_coords:
            cv2.rectangle(
                self._img_copy, coords[0], coords[1], CV_Window.COLOR
            )

    def _validate_coords(self, x, y):
        # Edge detection algorithm to ensure boxes do not overlap.
        count = 0
        for coords in self._bb_coords:
            if (
                    coords[COORDS_P.POINT2.value][COORDS_XY.X.value] < self._x
                    or
                    coords[COORDS_P.POINT1.value][COORDS_XY.X.value] > x
                    or
                    coords[COORDS_P.POINT2.value][COORDS_XY.Y.value] < self._y
                    or
                    coords[COORDS_P.POINT1.value][COORDS_XY.Y.value] > y
            ):
                count += 1
        if count == len(self._bb_coords):
            return True
        else:
            return False

    def accept_label_points(self):
        if not self._next_img and self.item_count > 0:
            return True
        else:
            return False

    def update_box(self, x, y):
        self.refresh_img()
        cv2.rectangle(
            self._img_copy,
            (self._x, self._y),
            (x, y),
            CV_Window.COLOR
        )
        self.show_image()

    def draw_cross(self, x, y):
        self.refresh_img()
        height, width, _ = self._img_copy.shape
        cv2.line(self._img_copy, (x, 0), (x, height), CV_Window.COLOR)
        cv2.line(self._img_copy, (0, y), (width, y), CV_Window.COLOR)
        self.show_image()

    def skip(self):
        print("skipping")
        self._next_img = True
        self._bb_coords = []

    def restart(self):
        print("restarting labeling process")
        self.item_count = 0
        self._bb_coords = []
        self.first_point = True

    def save_raw(self):
        # Save labeling data
        print("Writing to file")
        with open(Conf.LABEL_FILE, "a") as file:
            for key in self._coord_dict:
                line = "{} {} ".format(key, len(self._coord_dict[key]))
                for coords in self._coord_dict[key]:
                    width = (
                            coords[COORDS_P.POINT2.value][COORDS_XY.X.value]
                            - coords[COORDS_P.POINT1.value][COORDS_XY.X.value]
                    )
                    height = (
                            coords[COORDS_P.POINT2.value][COORDS_XY.Y.value]
                            - coords[COORDS_P.POINT1.value][COORDS_XY.Y.value]
                    )
                    line += "{} {} {} {} ".format(
                        coords[0][0], coords[0][1], width, height
                    )
                line += "\n"
                file.write(line)

    def finish(self):
        # Perform post operation clean up
        self.save_raw()
        if self._location is IMG_LOC_TYPE.CAM:
            self._cap.release()

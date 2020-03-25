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
from CV2_event_handler import mouse_events
from enums import IMG_LOC_TYPE, COORDS_P, COORDS_XY
from misc import add_text_to_img


class ImageHandler:
    """
    This class controls the behaviour of the image labeling system.
    """
    _inst = None

    def __init__(self):
        # Ensure the correct environment exist
        if not os.path.exists(Conf.CROPPED_IMG_FOLDER):
            os.mkdir(Conf.CROPPED_IMG_FOLDER)
        if not os.path.exists(Conf.DELETED_IMG_FOLDER):
            os.mkdir(Conf.DELETED_IMG_FOLDER)
        if not os.path.exists(Conf.LABELED_IMG_FOLDER):
            os.mkdir(Conf.LABELED_IMG_FOLDER)
        if os.listdir(Conf.LABELED_IMG_FOLDER):
            raise AssertionError(
                "The label folder is not empty. "
                f"Folder name: {Conf.LABELED_IMG_FOLDER}"
            )
        if not os.path.exists(Conf.ORIG_IMG_FOLDER):
            # If this folder does not exist there is nothing we can do
            raise FileNotFoundError(
                "The folder with the original images was not found. "
                f"Folder name: {Conf.ORIG_IMG_FOLDER}"
            )

        self.images = [img for img in os.listdir(Conf.ORIG_IMG_FOLDER)]
        self.num_images = len(self.images)
        self.num_labeled_images = 0
        # Number of processed
        self.index = 0
        # Number of items in the image
        self.item_count = 0
        # All the coordinates for the bounding box (bb)
        self.bb_coords = []
        # Each image name and the bb coordinates
        self.coord_dict = {}

        # Flags
        self.next_img = True
        self.first_point = True
        self.block_section = False
        self.end = False

        # Dummy initialize variables
        self.img = None
        self.img_copy = None
        self.img_name = None
        self.x = None
        self.y = None

        # Create OpenCV windows and set call back functions ##################
        cv2.namedWindow(CV_Window.MAIN_WINDOW)
        cv2.setMouseCallback(CV_Window.MAIN_WINDOW, mouse_events)

        # Create info window
        self.message_window = np.zeros(CV_Window.INFO_WINDOW_SIZE, np.uint8)
        for line, origin in CV_Window.INFO_LIST:
            cv2.putText(
                self.message_window,
                line,
                origin,
                CV_Window.FONT,
                CV_Window.FONT_SCALE,
                CV_Window.COLOR3,
                CV_Window.THICKNESS
            )
        cv2.imshow(CV_Window.INFO_WINDOW, self.message_window)

    @staticmethod
    def get_inst():
        # Allow all functions to use one instance of the class
        if ImageHandler._inst is None:
            ImageHandler._inst = ImageHandler()
        return ImageHandler._inst

    def show_image(self):
        if self.item_count == 0:
            self.get_new_img()
        cv2.imshow(CV_Window.MAIN_WINDOW, self.img_copy)

    def get_new_img(self):
        if self.next_img:
            self.next_img = False
            self.item_count = 0
            if self.index < self.num_images:
                print(
                    "Number of images remaining: "
                    f"{self.num_images - self.index}"
                )
                self.img_name = self.images[self.index]
                self.img = cv2.imread(
                    f"{Conf.ORIG_IMG_FOLDER}/{self.img_name}"
                )
                self.index += 1
            else:
                self.end = True
                return
            height, width, _ = self.img.shape
            if width > Conf.MAX_IMG_WIDTH:
                quotient = width / Conf.MAX_IMG_WIDTH
                width = Conf.MAX_IMG_WIDTH
                height = height / quotient
                height = int(height)
                self.img = cv2.resize(self.img, (width, height))
            self.img_copy = self.img.copy()
            cv2.putText(
                self.img_copy,
                self.img_name,
                CV_Window.NAME_ORG,
                CV_Window.FONT,
                CV_Window.FONT_SCALE,
                CV_Window.COLOR2,
                CV_Window.THICKNESS
            )
            cv2.imshow(CV_Window.MAIN_WINDOW, self.img_copy)

    def set_top_left(self, x, y):
        # The upper left corner of the bounding box
        self.x = x
        self.y = y
        self.first_point = False
        cv2.circle(self.img_copy, (x, y), 1, CV_Window.COLOR)

    def set_bottom_right(self, x, y):
        # Switch the points if they were placed in wrong order
        if self.x > x:
            temp_x = self.x
            self.x = x
            x = temp_x
        if self.y > y:
            temp_y = self.y
            self.y = y
            y = temp_y

        if self.validate_coords(x, y):
            self.first_point = True
            if self.block_section:
                cv2.rectangle(
                    self.img,
                    (self.x, self.y),
                    (x, y),
                    CV_Window.COLOR4,
                    -1
                )
                self.block_section = False
            else:
                self.bb_coords.append(((self.x, self.y), (x, y)))
                # Draw the bounding box
                cv2.rectangle(
                    self.img_copy,
                    (self.x, self.y),
                    (x, y),
                    CV_Window.COLOR,
                )
        else:
            print("Invalid coordinates, please re-enter them")
            self.refresh_img()
            self.first_point = True

    def save_labels(self):
        if self.bb_coords:
            print(f"Saving {self.img_name}")
            cv2.imwrite(f"{Conf.LABELED_IMG_FOLDER}/{self.img_name}", self.img)
            self.coord_dict[self.img_name] = self.bb_coords
            self.num_labeled_images += 1
            self.next_img = True
            self.bb_coords = []
        else:
            print("Cannot save because you have no bounding boxes defined")

    def refresh_img(self):
        self.img_copy = self.img.copy()
        cv2.putText(
            self.img_copy,
            self.img_name,
            CV_Window.NAME_ORG,
            CV_Window.FONT,
            CV_Window.FONT_SCALE,
            CV_Window.COLOR2,
            CV_Window.THICKNESS
        )
        for coords in self.bb_coords:
            cv2.rectangle(
                self.img_copy, coords[0], coords[1], CV_Window.COLOR
            )

    def validate_coords(self, x, y):
        # Edge detection algorithm to ensure boxes do not overlap.
        count = 0
        for coords in self.bb_coords:
            if (
                    coords[COORDS_P.POINT2.value][COORDS_XY.X.value] < self.x
                    or
                    coords[COORDS_P.POINT1.value][COORDS_XY.X.value] > x
                    or
                    coords[COORDS_P.POINT2.value][COORDS_XY.Y.value] < self.y
                    or
                    coords[COORDS_P.POINT1.value][COORDS_XY.Y.value] > y
            ):
                count += 1
        if count == len(self.bb_coords):
            return True
        else:
            return False

    def update_box(self, x, y):
        self.refresh_img()
        if self.block_section:
            color = CV_Window.COLOR4
        else:
            color = CV_Window.COLOR
        cv2.rectangle(
            self.img_copy,
            (self.x, self.y),
            (x, y),
            color
        )
        self.show_image()

    def draw_cross(self, x, y):
        self.refresh_img()
        if self.block_section:
            color = CV_Window.COLOR4
        else:
            color = CV_Window.COLOR
        height, width, _ = self.img_copy.shape
        cv2.line(self.img_copy, (x, 0), (x, height), color)
        cv2.line(self.img_copy, (0, y), (width, y), color)
        self.show_image()

    def skip(self):
        print("skipping")
        self.next_img = True
        self.bb_coords = []

    def restart(self):
        print("restarting labeling process")
        self.item_count = 0
        self.bb_coords = []
        self.first_point = True

    def delete_img(self):
        print(f"Moving {self.img_name} to deletion folder")
        os.rename(
            f"{Conf.ORIG_IMG_FOLDER}/{self.img_name}",
            f"{Conf.DELETED_IMG_FOLDER}/{self.img_name}"
        )
        self.next_img = True
        self.bb_coords = []

    def save_label_file(self):
        # Save labeling data
        if self.coord_dict != {}:
            print("Writing to file")
            print(f"{self.num_labeled_images} images labeled")
            with open(Conf.LABEL_FILE, "a") as file:
                for key in self.coord_dict:
                    line = "{} {} ".format(key, len(self.coord_dict[key]))
                    for coords in self.coord_dict[key]:
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


def validate_labled_images():
    if not os.listdir(Conf.LABELED_IMG_FOLDER):
        raise AssertionError(
            "The label folder is empty. "
            f"Folder name: {Conf.LABELED_IMG_FOLDER}"
        )

    labeled_images = {}
    with open(f"{Conf.LABELED_IMG_FOLDER}/info.lst") as file:
        line = file.readline()
        while line:
            segments = line.split(" ")
            name = segments[0]
            num_labels = int(segments[1])
            segments = segments[2:]
            x1 = []
            x2 = []
            y1 = []
            y2 = []
            for i in range(num_labels):
                x1.append(int(segments[0]))
                y1.append(int(segments[1]))
                x2.append(int(segments[0]) + int(segments[2]))
                y2.append(int(segments[1]) + int(segments[3]))
                segments = segments[4:]
            top_left = list(zip(x1, y1))
            bottom_right = list(zip(x2, y2))
            labeled_images[name] = [num_labels, top_left, bottom_right]
            line = file.readline()

    for key in labeled_images:
        img = cv2.imread(f"{Conf.LABELED_IMG_FOLDER}/{key}")
        for i in range(labeled_images[key][0]):
            print(labeled_images[key][1][i])
            cv2.rectangle(
                img,
                labeled_images[key][1][i],
                labeled_images[key][2][i],
                CV_Window.COLOR,
                CV_Window.THICKNESS
            )
        cv2.imshow(CV_Window.MAIN_WINDOW, img)
        k = cv2.waitKey()
        # incomplete
    cv2.destroyAllWindows()

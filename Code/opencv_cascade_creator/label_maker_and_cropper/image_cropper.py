""" Kuwin Wyke
Midwestern State University

This module contains the image cropper class that is used to take already
labeled images and crop out the item. The cropped image is then resized to
the final desired size of the positive objects
"""
import cv2
import os

from config import Conf, CV_Window


def cut_out_objects():
    image_cropper = ImageCropper.get_inst()
    image_cropper.show_image()


class ImageCropper:
    """This class is used to crop out already labeled images"""
    _inst = None

    def __init__(self):
        self._labels = {}
        if not os.path.exists(Conf.IMG_PATH_CROP):
            os.mkdir(Conf.IMG_PATH_CROP)
        with open(Conf.LABEL_FILE) as file:
            line = file.readline()
            while line != "":
                temp = line.split(" ")
                if temp[-1] == "\n":
                    temp.pop()
                # Basic validation to ensure the number of coordinates is
                # correct
                if int(temp[1]) * 4 == len(temp) - 2:
                    name = temp[0]
                    num_labels = int(temp[1])
                    temp.pop(0)
                    temp.pop(0)
                    self._labels[name] = [num_labels]
                    for _ in range(num_labels):
                        # Save top left coordinates
                        # and the width and height
                        try:
                            self._labels[name].append(
                                [
                                    (int(temp[0]), int(temp[1])),
                                    (int(temp[2]), int(temp[3]))
                                ]
                            )
                            # Remove values that were just recorded
                            temp.pop(0)
                            temp.pop(0)
                            temp.pop(0)
                            temp.pop(0)
                        except ValueError:
                            print("{} not a valid name".format(name))
                else:
                    print("Malformed string --> {}".format(line))
                line = file.readline()

    @staticmethod
    def get_inst():
        if ImageCropper._inst is None:
            ImageCropper._inst = ImageCropper()
        return ImageCropper._inst

    def show_image(self):
        index = 0
        for key in self._labels:
            print(key, self._labels[key])
            img = cv2.imread(Conf.IMG_PATH + "/" + key, cv2.IMREAD_GRAYSCALE)
            num_labels = self._labels[key][0]
            for i in range(num_labels):
                x, y = self._labels[key][i+1][0]
                width, height = self._labels[key][i+1][1]
                crop_img = img[y:y+height, x:x+width]
                crop_img = cv2.resize(
                    crop_img, (Conf.CROP_SIZE, Conf.CROP_SIZE)
                )
                cv2.rectangle(
                    img, (x, y), (x + width, y + height), CV_Window.COLOR
                )
                name = Conf.IMG_PATH_CROP + "/_crop" + str(index) + ".jpg"
                cv2.imwrite(name, crop_img)
                index += 1

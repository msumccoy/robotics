""" Kuwin Wyke
Midwestern State University

This module contains the image cropper class that is used to take already
labeled images and crop out the item. The cropped image is then resized to
the final desired size of the positive objects
"""
import cv2

from config import Conf, CamConf, CV_Window


def cut_out_objects():
    image_cropper = ImageCropper.get_inst()
    image_cropper.show_image()


class ImageCropper:
    """This class is used to crop out already labeled images"""
    _inst = None

    def __init__(self):
        self._labels = {}
        with open(Conf.RAW_LABEL_FILE) as file:
            line = file.readline()
            while line != "":
                temp = line.split(" ")
                if temp[-1] == "\n":
                    temp.pop()
                # Basic validation to ensure the number of coordinates is
                # correct
                if int(temp[1]) * 4 == len(temp) - 2:
                    name = temp[0]
                    if "_cam" in name or "_file" in name:
                        num_labels = int(temp[1])
                        temp.pop(0)
                        temp.pop(0)
                        self._labels[name] = [num_labels]
                        for _ in range(num_labels):
                            # Save top left coordinates
                            # and the width and height
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
            img = cv2.imread(key, cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (CamConf.RESIZE, CamConf.RESIZE))
            num_labels = self._labels[key][0]
            for i in range(num_labels):
                x, y = self._labels[key][i+1][0]
                width, height = self._labels[key][i+1][1]
                print(key)
                crop_img = img[y:y+height, x:x+width]
                crop_img = cv2.resize(
                    crop_img, (Conf.FINAL_POS_SIZE, Conf.FINAL_POS_SIZE)
                )
                cv2.rectangle(
                    img, (x, y), (x + width, y + height), CV_Window.COLOR
                )
            name = Conf.IMG_PATH + "_crop" + str(index) + ".jpg"
            cv2.imwrite(name, crop_img)
            index += 1
            with open(Conf.FULL_LABEL_FILE, "a") as file:
                line = "{} 1 0 0 {} {}\n".format(
                    name, Conf.FINAL_POS_SIZE, Conf.FINAL_POS_SIZE
                )
                file.write(line)

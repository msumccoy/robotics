""" Kuwin Wyke
Midwestern State University

This program is used to label images then cut images out of those labeled
images to be used with the opencv program written in C++.

Incomplete
"""
from config import Conf
from enums import IMG_LOC_TYPE
from image_cropper import cut_out_objects
from label_images import label_images


def main():
    # Clear the file to ensure it is empty for writing
    # with open(Conf.RAW_LABEL_FILE, "w") as file:
    #     pass
    # label_images(IMG_LOC_TYPE.CAM)
    label_images(IMG_LOC_TYPE.FILE)
    cut_out_objects()


if __name__ == '__main__':
    main()

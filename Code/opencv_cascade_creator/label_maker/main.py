""" Kuwin Wyke
Midwestern State University

This program is used to label images then cut images out of those labeled
images to be used with the opencv program written in C++.

Incomplete
"""
from enums import IMG_LOC_TYPE
from label_images import label_images


def main():
    label_images(IMG_LOC_TYPE.CAM)
    # label_images(IMG_LOC_TYPE.FILE)


if __name__ == '__main__':
    main()

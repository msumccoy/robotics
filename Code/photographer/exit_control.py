""" Kuwin Wyke
Midwestern State University
Start: 23 December 2019
End: work in progress

***Description to be made***
"""

import cv2
import os

from variables import General
from constants import GeneralConst


def get_dist(file_name):
    name_len = len(file_name)
    dist = name_len
    for i in range(10):
        location = file_name.find(str(i))
        if location != -1 and dist > location:
            dist = location
    dist -= name_len
    return dist


def get_new_file_name():
    for root, dir, files in os.walk(GeneralConst.PATH):
        try:
            file = files[-1]
        except IndexError as e:
            return GeneralConst.PATH + "ball1.jpg"
        target_file_index = 0
        file_name, file_type = files[0].split(".")
        dist = get_dist(file_name)
        max_val = int(file_name[dist:])
        for file in files:
            file_name, file_type = file.split(".")
            dist = get_dist(file_name)
            if int(file_name[dist:]) > max_val:
                max_val = int(file_name[dist:])
                target_file_index = files.index(file)
        file = files[target_file_index]
        file_name, file_type = file.split(".")
        dist = get_dist(file_name)
        file_num = str(int(file_name[dist:]) + 1)
        file_name = (
            GeneralConst.PATH
            + file_name[:dist] + str(file_num) + "." + file_type)
    return file_name


def trigger_exit(control, opencv_img):
    if control == ord("x"):
        General.exit_code = 1
    elif control == ord("s"):
        file = get_new_file_name()
        print(file)
        cv2.imwrite(file, opencv_img)
    elif control == ord("1"):
        file = get_new_file_name()
        print(file)
        cv2.imwrite(file, opencv_img)
        General.exit_code = 1

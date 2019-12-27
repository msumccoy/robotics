""" Kuwin Wyke
Midwestern State University
Start: 26 December 2019
End: work in progress

***Description to be made***
"""


import urllib.request
import cv2
import numpy as np
import os

from config import Conf


def store_raw_images():
    # neg_image_urls = (  # replaced with text file
    #     urllib.request.urlopen(Conf.neg_images_link).read().decode())
    neg_image_urls = open(Conf.neg_image_urls).read()
    pic_num = 2000

    if not os.path.exists(Conf.neg_folder):
        os.makedirs(Conf.neg_folder)

    for i in neg_image_urls.split('\n'):
        try:
            print(i)
            urllib.request.urlretrieve(
                i, Conf.neg_folder + str(pic_num) + Conf.im_type)
            img = cv2.imread(
                Conf.neg_folder + str(pic_num) + Conf.im_type,
                cv2.IMREAD_GRAYSCALE)
            # should be larger than samples / pos pic
            # (so we can place our image on it)
            resized_image = cv2.resize(img, (Conf.neg_size, Conf.neg_size))
            cv2.imwrite(
                Conf.neg_folder + str(pic_num) + Conf.im_type, resized_image)
            pic_num += 1

        except Exception as e:
            print(str(e))

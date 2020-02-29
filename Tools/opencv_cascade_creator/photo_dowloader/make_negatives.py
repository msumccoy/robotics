""" Kuwin Wyke
Midwestern State University

This module is used to download negative images from the internet.
The module
"""

import urllib.request
import cv2
import numpy as np
import os
import threading
import multiprocessing
import time
from datetime import datetime

import misc
from config import Conf, LogConf
from enums import StatusEnums
from log_master import LogMaster


@misc.timer
def download_negatives_and_create_text_file():
    # Use threading to make the process faster
    retrieval_workers = [
        threading.Thread(
            target=get_images, kwargs={"output_name": "thread {}".format(i)}
        )
        for i in range(Conf.NUM_WORKERS)
    ]  # This is called a list comprehension

    # Start the threads and wait for them to complete
    for worker in retrieval_workers:
        worker.start()
    for worker in retrieval_workers:
        worker.join()

    validate_images()


class PicNumMaster:
    _inst = None
    _lock = threading.Lock()

    def __init__(self):
        self._pic_num = self._get_first_pic_num()

    @staticmethod
    def get_inst():
        # Create a function to allow all threads to use the same instance of
        # the class
        with PicNumMaster._lock:
            # Use lock to prevent a race condition that allows threads to get
            # a different instance of the class
            if PicNumMaster._inst is None:
                PicNumMaster._inst = PicNumMaster()
            return PicNumMaster._inst

    @staticmethod
    def _get_first_pic_num():
        num = 0
        if not os.path.exists(Conf.NEG_FOLDER):
            os.makedirs(Conf.NEG_FOLDER)
            return num
        files = os.listdir(Conf.NEG_FOLDER)
        num_files = len(files)
        if num_files == 0:
            return num
        range_files = range(num_files)

        for root, dirs, files in os.walk(Conf.NEG_FOLDER):
            range_files = range(len(files))

        num = range_files[-1] + 1
        return num

    def get_next_pic_num(self):
        with self._lock:
            # Use a lock to prevent more than one thread from getting the same
            # number
            num = self._pic_num
            self._pic_num += 1
            return num


def validate_images(wait=1):
    image_list = os.listdir(Conf.NEG_FOLDER)
    for image in image_list:
        image_with_path = Conf.NEG_FOLDER + image
        img = cv2.imread(image_with_path)
        try:
            cv2.imshow("image", img)
        except cv2.error as e:
            os.remove(image_with_path)
            print(
                "{} was removed because of error {}".format(
                    image_with_path, e
                )
            )
        k = cv2.waitKey(wait)
        if k == 27:
            break
    cv2.destroyAllWindows()
    with open(Conf.NEG_FILE, "w") as file:
        for img in os.listdir(Conf.NEG_FOLDER):
            line = Conf.NEG_FOLDER + img + "\n"
            file.write(line)


class URL_Retrieval:
    _inst = None
    _lock = threading.Lock()

    def __init__(self):
        self._neg_image_urls = []
        self._url = None
        self._index = 0

        all_files = [
            Conf.NEG_URLS_FOLDER + file
            for file in os.listdir(Conf.NEG_URLS_FOLDER)
        ]
        for file in all_files:
            with open(file) as url_file:
                end = False
                while not end:
                    try:
                        line = url_file.readline()
                        end = True
                    except Exception as e:
                        print(e)
                while line != "":
                    self._neg_image_urls.append(line[:-1])
                    try:
                        line = url_file.readline()
                    except Exception as e:
                        print(e)
                        line = "none"

    @staticmethod
    def get_inst():
        # Create a function to allow all threads to use the same instance of
        # the class
        with URL_Retrieval._lock:
            # Use lock to prevent a race condition that allows threads to get
            # a different instance of the class
            if URL_Retrieval._inst is None:
                URL_Retrieval._inst = URL_Retrieval()
            return URL_Retrieval._inst

    def get_next_url(self):
        with self._lock:
            print("url index ", self._index)
            if self._index < len(self._neg_image_urls):
                url = self._neg_image_urls[self._index]
                self._index += 1
                return url
            else:
                return -1


@misc.timer
def download_image(url, file_name):
    # Primary task of each thread that is run in a separate process
    logger = LogMaster.get_inst()
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_name = Conf.NEG_FOLDER + file_name
    try:
        urllib.request.urlretrieve(url, file_name)
        img = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
        resized_image = cv2.resize(img, (Conf.NEG_SIZE, Conf.NEG_SIZE))
        cv2.imwrite(file_name, resized_image)
        message = LogConf.T_SUCCESS.substitute(date_t=date_time, url=url)
        logger.log(message)
        return StatusEnums.SUCCESS
    except Exception as e:
        if e.__str__()[-1:] == "\n":
            e = e.__str__()[:-2]
        message = LogConf.T_ERROR.substitute(
            date_t=date_time, url=url, error=e
        )
        logger.log(message)
        return StatusEnums.FAILURE


@misc.timer
def get_images():
    pic_num = PicNumMaster.get_inst()
    url_links = URL_Retrieval.get_inst()
    logger = LogMaster.get_inst()
    # Allow one extra process to be made
    pool = multiprocessing.Pool(1)

    url = url_links.get_next_url()
    pic_name = str(pic_num.get_next_pic_num()) + Conf.IMG_TYPE
    change_pic_name = True
    while url != -1:
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Create independent process
        download_results = pool.apply_async(
            download_image, (url, pic_name), {"output_name": url}
        )
        try:
            result = download_results.get(Conf.DOWNLOAD_TIMEOUT)
            if result is StatusEnums.FAILURE:
                change_pic_name = False
        except multiprocessing.context.TimeoutError:
            change_pic_name = False
            message = LogConf.T_TIMEOUT.substitute(date_t=date_time, url=url)
            logger.log(message)

        url = url_links.get_next_url()
        if change_pic_name:
            pic_name = str(pic_num.get_next_pic_num()) + Conf.IMG_TYPE
        else:
            change_pic_name = True


if __name__ == "__main__":
    download_negatives_and_create_text_file(
        output_name="negatives_main_thread"
    )

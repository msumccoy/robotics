""" Kuwin Wyke
Midwestern State University

This module contains the constants/configurations necessary for the downloads
"""
import multiprocessing
from string import Template


class Conf:
    NEG_URLS_FOLDER = "urls/negative_urls/"
    NEG_FOLDER = 'neg/'
    NEG_SIZE = 300
    NEG_FILE = "negatives.txt"
    IMG_TYPE = ".jpg"

    POS_FOLDER = "pos"
    POS_SIZE = NEG_SIZE / 2

    DOWNLOAD_TIMEOUT = 120
    NUM_WORKERS = 10
    LOCK = multiprocessing.Lock()


class LogConf:
    PATH = "logs/"
    FILE = "download_log.txt"

    MESSAGE_TYPES = {
        "success": "Success",
        "err": "Error",
        "info": "info"
    }

    T_TIMEOUT = Template(
        "$date_t {}: $url timed out and had to be terminated\n".format(
            MESSAGE_TYPES["err"]
        )
    )
    T_ERROR = Template(
        "$date_t {}: There was an error downloading $url.\n"
        "$date_t {}: $error\n".format(
            MESSAGE_TYPES["err"], MESSAGE_TYPES["err"]
        )
    )
    T_SUCCESS = Template(
        "$date_t {}: $url downloaded successfully\n".format(
            MESSAGE_TYPES["success"]
        )
    )
    T_THREAD_COMPLETE = Template(
        "$date_t {}: $thread completed in $dur seconds\n".format(
            MESSAGE_TYPES["info"]
        )
    )


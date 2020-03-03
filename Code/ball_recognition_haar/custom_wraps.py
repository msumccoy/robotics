"""
Kuwin Wyke
Midwester State University

This module contains special wrappers that are used within this project.
"""
import time
import logging
from functools import wraps

from ball_recognition_haar.config import Log
from ball_recognition_haar.log_frequency_control import LogFrequency


logger = logging.getLogger(Log.NAME)


def time_wrapper(orig_func):
    # This function calculates the time taken to execute a function and logs
    # it the information to file.
    @wraps(orig_func)
    def wrapper(*args, name=orig_func.__name__, **kwargs):
        frequency_check = LogFrequency.get_inst(name)
        start_time = time.time()
        return_value = orig_func(*args, **kwargs)
        end_time = time.time() - start_time
        message = "{} executed in {:.3f} seconds".format(name, end_time)
        logger.debug(message)
        if frequency_check.check_interval():
            logger.info(message)
        return return_value
    return wrapper

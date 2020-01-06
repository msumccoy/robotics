import serial
import time

from config import Conf


def clear_cache(ser, wait=.05):
    a = ""
    while a == "":
        a = ser.read()
    time.sleep(wait)


def send_cmd(ser, hex_cmd, cache_wait=.05):
    if hex_cmd in Conf.HEX_DICT:
        message = Conf.HEX_DICT[hex_cmd]
    else:
        message = "Motion"
    # print("Motion command {}: {}".format(message, hex_cmd))
    ser.write(hex_cmd)
    clear_cache(ser, cache_wait)


def get_int(message):
    not_exit = 1
    while not_exit:
        try:
            input_num = input(message)
            num = int(input_num)
            not_exit = 0
        except TypeError:
            print("{} is not a valid number".format(input_num))
            print("Enter a valid number")
    return num

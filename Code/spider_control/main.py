import serial
import sys
import time

import misc
import variables
from config import Conf
from play_motion import play_rcb4_motion


def main():
    ser = serial.Serial(
        Conf.SPIDER_PORT,
        Conf.BAUDRATE,
        Conf.BYTESIZE,
        Conf.PARITY,
        Conf.STOPBITS,
        Conf.TIMEOUT,
    )

    while not ser.isOpen():
        ser.Open()
    time.sleep(.05)

    print("Initializing ", Conf.STOP)
    misc.send_cmd(ser, Conf.STOP, .1)

    while variables.not_exit:
        num = misc.get_int("Enter a motion number: ")
        if num == -1:
            print("Stopping motion")
            misc.send_cmd(ser, Conf.STOP)
        elif num == -2:
            print("Setting to home position")
            time.sleep(1)
            misc.send_cmd(ser, Conf.STOP)
            play_rcb4_motion(ser, 17, 1)
        elif num < 0:
            misc.send_cmd(ser, Conf.STOP)
            variables.not_exit = 0
        else:
            play_rcb4_motion(ser, num, 1)

    print("Closing connection")
    ser.flush()
    ser.close()


if __name__ == '__main__':
    main()

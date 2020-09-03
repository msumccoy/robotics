import serial


class Conf:
    VERSION = "1.0"

    # serial config
    HUMANOID_PORT = "/dev/rfcomm1"
    SPIDER_PORT = "/dev/rfcomm2"
    BAUDRATE = 9600
    BYTESIZE = serial.EIGHTBITS
    PARITY = serial.PARITY_EVEN
    STOPBITS = serial.STOPBITS_ONE
    SER_TIMEOUT = 1

    # Cameras Constants
    SET_WIDTH = 320
    SET_HEIGHT = 240

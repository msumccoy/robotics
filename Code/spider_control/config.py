import serial


class Conf:
    # serial config
    SPIDER_PORT = "/dev/rfcomm2"
    BAUDRATE = 9600
    BYTESIZE = serial.EIGHTBITS
    PARITY = serial.PARITY_EVEN
    STOPBITS = serial.STOPBITS_ONE
    TIMEOUT = 1

    # Hex Commands
    STOP = "\x09\x00\x02\x00\x00\x00\x10\x83\x9e"
    RESET = (
        "\x11\x00\x02\x02\x00\x00\x4b\x04"
        "\x00\x00\x00\x00\x00\x00\x00\x00\x64"
    )
    RESUME = "\x09\x00\x02\x00\x00\x00\x13\x83\xa1"

    ACK_COMMAND = "\x04\xfe\x06\x08"
    GET_OPTIONS = "\x0a\x00\x20\x00\x00\x00\x00\x00\x02\x2c"

    # hex dictionary
    HEX_DICT = {
        STOP: "stop motion",
        RESET: "Reset",
        RESUME: "Resume",
    }

    """
    0  up and down
    1 forward slightly
    2 back slightly
    3 turn left slightly (fast)
    4 turn right slightly (fast)
    5 forward 6 steps (slow)
    6 back 6 steps (slow)
    7 turn left (slow mid turn)
    8 turn right (slow mid turn)
    9 prance
    10 dance 
    up on hind-legs and wave; forward slightly; back slightly; wiggle;
    up on hind-legs move front legs up and down
    11 dance 
    up and down several times; fast prance; wiggle
    12 turn right (slow big turn)
    13 turn left (slow big turn)
    14 forward then back (fast)
    15 dance (wiggle then remain mid height)
    16 slow wiggle
    17 stand mid height
    18 forward 3 steps (slow remain mid height)
    19 back 3 steps (slow remain mid height)
    20 forward continuously 
    21 turn right continuously
    22 turn left continuously
    23 forward continuously
    29 wave front right paw (continuous?)
    """

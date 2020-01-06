import sys
import time
import serial

from config import Conf
import misc


def play_rcb4_motion(ser, motion_num, wait=0):
    try:
        misc.send_cmd(ser, Conf.STOP)

        misc.send_cmd(ser, Conf.RESET)

        motion_string = make_motion_cmd(motion_num)
        misc.send_cmd(ser, motion_string)

        misc.send_cmd(ser, Conf.RESUME)

        ser.flush()
    except serial.SerialException:
        ser.flush()
        ser.close()
        sys.exit()

    print("Sleeping", wait)
    time.sleep(wait)

    print("Done.")


def make_motion_cmd(motion_num):
    # Motion numbers start at position 11 with 8 spaces (bytes) between
    # in Heart2Heart
    motion_hex = (int(motion_num) * 8) + 11
    # remove "0x" from hex conversion
    motion_hex = hex(motion_hex)[2:]
    # Make motion number 4 bytes if it is less than 4 bytes by adding 0
    while len(motion_hex) < 4:
        motion_hex = "0" + motion_hex
    # Generate warning (not expected to be used)
    if len(motion_hex) > 4:
        print("Generate Motion - warning!!! length greater than 4")

    # Lower byte is last two digits of motion hex
    motion_hex_lower = motion_hex[-2:]
    # print(motion_hex_lower)
    # Higher byte is the two digits before the last of motion hex
    motion_hex_higher = motion_hex[-4:-2]
    # print(motion_hex_higher)

    # Get the sum of all integer values for the robot to verify all bytes
    # arrived
    check_sum = (int(motion_hex_lower, 16) + int(motion_hex_higher, 16)
                 # 147 = int("07", 16) + int("0c", 16) + int("80", 16)
                 + 147)
    # Convert check sum to hex and take last 2 digits
    check_sum = str(hex(check_sum)[-2:])
    command_string = (r"\x07\x0c\x80"
                      + r'\x' + motion_hex_lower
                      + r'\x' + motion_hex_higher
                      + r"\x00\x" + check_sum)
    return command_string.decode("string_escape")

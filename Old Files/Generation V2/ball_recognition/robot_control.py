""" Kuwin Wyke
Midwestern State University
Start: 6 November 2019
End: work in progress

This module is designed to be used in the ball recognition program in the
folder named "ball_recognition_v1". It contains a class to connect to the
robot, a function to control the robot through object detection and a function
to control the robot manually.
"""

import serial
import time

# Project specific modules
from variables import ExitControl, RobotCom
from config import Conf
from constants import HexConst, Locks, SerConst
from debug import Debug


# Create class to handle robot object
class Robot:
    """ This class is used to create a connection with the robot via the
    serial module and bluetooth on the raspberry pi. Once closed this class
    will automatically close the connection with the robot.
    """
    _inst1 = None
    _inst2 = None

    @staticmethod
    def get_inst(robot_type):
        if robot_type == 1:
            if Robot._inst1 is None:
                Robot._inst1 = Robot(1)
            return Robot._inst1
        elif robot_type == 2:
            if Robot._inst2 is None:
                Robot._inst2 = Robot(2)
            return Robot._inst2
        else:
            raise ValueError(
                "{} is not a valid option for Robot".format(robot_type))

    def __init__(self, robot_type):
        if robot_type == 1:
            com_port = Conf.HUMANOID_PORT
            print("Initializing Humanoid")
        else:
            com_port = Conf.SPIDER_PORT
            print("Initializing spider")

        # Create serial port object for connection to the robot
        self.ser = serial.Serial(
            com_port,
            Conf.BAUDRATE,
            Conf.BYTESIZE,
            Conf.PARITY,
            timeout=Conf.SER_TIMEOUT
        )
        start_time = time.time()
        # Loop until serial connection made or connection times out
        print(self.ser.isOpen())
        while not self.ser.isOpen():
            if (time.time() - start_time) > SerConst.PORT_TIME_OUT:
                raise Exception("Connection timed out")
            self.ser.Open()
        if Debug.robot:
            print("The connection took ", time.time() - start_time, "seconds")

    def play_rcb4_motion(self, motion_cmd):
        with Locks.ROBOT_LOCK:
            try:
                self.send_motion_cmd(HexConst.STOP)
                self.send_motion_cmd(HexConst.RESET)
                print("motion command ", motion_cmd)
                self.send_motion_cmd(motion_cmd)
                self.send_motion_cmd(HexConst.RESUME)
                self.ser.flush()
            except serial.SerialException as e:
                self.ser.flush()
                print("A serial exception was hit: {}".format(e))

    def send_motion_cmd(self, hex_cmd, cache_wait=.05):
        if Debug.robot:
            print("sending motion command: {}".format(hex_cmd))
        # with Locks.ROBOT_LOCK:
        self.ser.write(hex_cmd)
        self.clear_cache(cache_wait)

    def clear_cache(self, wait=.05):
        if Debug.robot:
            print("Clearing cache with wait time {}sec".format(wait))
        check = ""
        while check == "":
            check = self.ser.read()
        time.sleep(wait)

    @staticmethod
    def get_motion_cmd(motion_num):
        if motion_num in HexConst.HUMANOID_MOTION_DICT:
            return HexConst.HUNDRED_NUM_DICT[motion_num]
        else:
            print("Motion number {} not allowed".format(motion_num))
            return HexConst.STOP

    @staticmethod
    def generate_motion_cmd(motion_number):
        """
        This function potentially can't be used in python 3

        This function is used to generate a custom hex string for the
        robot.
        :param motion_number: This is a valid number that is programmed in
        heart2heart.
        :return command_string: return custom hex string for robot command
        """
        # Motion numbers start at position 11 with 8 spaces (bytes) between
        # in Heart2Heart
        motion_hex = (int(motion_number) * 8) + 11
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
        return command_string

    @staticmethod
    def background_control(robot_type):
        """ This function is to be used to send commands to the robot."""
        # Create robot object to initiate connection with the robot
        robot = Robot.get_inst(robot_type)
        print("robot robot robot ", robot)

        # Set to default state
        motion_num = -1
        while not ExitControl.gen:
            # Determine if motion command has been issued
            with Locks.ROBOT_LOCK:
                if RobotCom.motion_num != -1:
                    motion_num = RobotCom.motion_num
                    if type(motion_num) is int:
                        motion_num = Robot.get_motion_cmd(motion_num)
            # Send issued motion command without tying up the shared variable
            if motion_num != -1:
                robot.play_rcb4_motion(motion_num)
                print("send complete")
                motion_num = -1
                with Locks.ROBOT_LOCK:
                    RobotCom.motion_num = -1

    def __del__(self):
        # Destructor. This function is called when an object is deleted or the
        # program ends
        self.ser.flush()
        self.ser.close()

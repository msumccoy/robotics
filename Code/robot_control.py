"""
Kuwin Wyke
Midwestern State University
"""
import logging
import time

import serial

from config import Conf
from enums import RobotType
from misc import get_int
from variables import ExitControl


class Robot:
    _inst = {}
    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)

    @staticmethod
    def get_inst(robot_type):
        if robot_type != RobotType.HUMAN and robot_type != RobotType.SPIDER:
            raise ValueError(
                f"{robot_type} is not a valid option for robot type"
            )
        if robot_type not in Robot._inst:
            Robot._inst[robot_type] = Robot(robot_type)
        return Robot._inst[robot_type]

    def __init__(self, robot_type):
        self.start_time = time.time()
        if robot_type == RobotType.HUMAN:
            com_port = Conf.HUMANOID_PORT
            self.main_logger.info("Initializing Humanoid")
        elif robot_type == RobotType.SPIDER:
            com_port = Conf.SPIDER_PORT
            self.main_logger.info("Initializing spider")
        else:
            raise ValueError(
                f"{robot_type} is not a valid option for robot type"
            )
        self.robot_type = robot_type
        self.active_auto_control = True

        # Create serial port object for connection to the robot
        self.ser = serial.Serial(
            com_port,
            Conf.BAUDRATE,
            Conf.BYTESIZE,
            Conf.PARITY,
            timeout=Conf.SER_TIMEOUT
        )

        # Loop until serial connection made or connection times out
        duration = time.time() - self.start_time
        while not self.ser.isOpen():
            if duration > Conf.PORT_TIME_OUT:
                raise Exception("Connection timed out")
            self.ser.Open()
            duration = time.time() - self.start_time
        self.main_logger.debug(f"Connected after {duration} seconds")

    def send_command(self, motion_cmd):
        if type(motion_cmd) == int:
            motion_cmd = self.get_hex_cmd(motion_cmd)
        if self.robot_type == RobotType.HUMAN:
            lock = Conf.HUMANOID_LOCK
        elif self.robot_type == RobotType.SPIDER:
            lock = Conf.SPIDER_LOCK

        with lock:
            try:
                self.send_sub_command(Conf.HEX_STOP)
                self.send_sub_command(Conf.HEX_RESET)
                self.main_logger.debug("motion command ", motion_cmd)
                self.send_sub_command(motion_cmd)
                self.send_sub_command(Conf.HEX_RESUME)
                self.ser.flush()
            except serial.SerialException as e:
                self.ser.flush()
                self.main_logger.exception(f"Serial exception hit: {e}")

    def send_sub_command(self, hex_cmd, cache_wait=0.05):
        self.main_logger.debug(f"sending motion command: {hex_cmd}")
        self.ser.write(hex_cmd)
        self.clear_cache(cache_wait)

    def clear_cache(self, wait):
        self.main_logger.debug(f"clearing cache with wait time {wait}sec")
        check = ""
        while check == "":
            check = self.ser.read()
        time.sleep(wait)

    def get_hex_cmd(self, motion_num):
        valid = False
        if self.robot_type == RobotType.HUMAN:
            if motion_num in Conf.HUMANOID_FULL:
                valid = True
        elif self.robot_type == RobotType.SPIDER:
            if motion_num in Conf.HUMANOID_FULL:
                valid = True

        if valid:
            return Conf.HEX_HUNDRED_NUM[motion_num]
        else:
            self.main_logger.info(f"Motion number {motion_num} not allowed")
            return Conf.HEX_STOP


def manual_robot_control(robot_type):
    if robot_type == RobotType.HUMAN:
        full_dict = Conf.HUMANOID_FULL
        short_dict = Conf.HUMANOID_MOTION
    elif robot_type == RobotType.SPIDER:
        full_dict = short_dict= Conf.SPIDER_FULL
    else:
        raise ValueError(f"{robot_type} is not a valid robot type")

    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
    robot = Robot.get_inst(robot_type)
    full_control = False
    while not ExitControl.gen:
        command = input("Enter a Command or motion number: ")
        if command == Conf.CMD_FULL_CONTROL:
            full_control = not full_control
            main_logger.info(
                f"Full control Toggled: full_control = {full_control}"
            )
        elif command == Conf.CMD_REMOTE:
            main_logger.error("remote not implemented")
        elif command == Conf.CMD_CALIBRATE:
            main_logger.error("calibrate not implemented")
        elif command == Conf.CMD_CALIBRATE_STOP:
            main_logger.error("calibrate stop not implemented")
        elif command == Conf.CMD_DETECT_ON:
            robot.active_auto_control = True
        elif command == Conf.CMD_DETECT_OFF:
            robot.active_auto_control = False
        elif command == Conf.CMD_EXIT or command == Conf.CMD_EXIT:
            ExitControl.gen = True
            main_logger.info("Manual control exiting program")
        else:
            try:
                command = int(command)
            except ValueError:
                main_logger.debug(f"{command} is an unknown command")

            if full_control:
                if command in full_dict:
                    robot.send_command(command)
                else:
                    main_logger.debug(
                        f"{command} is an unknown motion number"
                    )
            elif command in short_dict:
                robot.send_command(command)
            else:
                main_logger.debug(f"{command} is an unknown motion number")


if __name__ == "__main__":
    # This section is to be used to test functions/methods of this file
    manual_robot_control(RobotType.SPIDER)

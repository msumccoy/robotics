"""
Kuwin Wyke
Midwestern State University
"""
import logging
import time

import serial

from config import Conf
from enums import RobotType
from misc import get_int, pretty_time
from variables import ExitControl


class Robot:
    _inst = {}
    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
    logger = logging.getLogger(Conf.LOG_ROBOT_NAME)

    @staticmethod
    def get_inst(robot_type):
        if robot_type not in Robot._inst:
            Robot._inst[robot_type] = Robot(robot_type)
        return Robot._inst[robot_type]

    def __init__(self, robot_type):
        self.main_logger.info(f"Robot started on version {Conf.VERSION}")
        self.logger.info(
            f"Robot started on version {Conf.VERSION}:\n"
            f"- robot_type: {robot_type}\n"
        )
        self.start = time.time()
        if robot_type != RobotType.HUMAN and robot_type != RobotType.SPIDER:
            raise ValueError(
                f"{robot_type} is not a valid option for robot type"
            )
        if robot_type == RobotType.HUMAN:
            com_port = Conf.HUMANOID_PORT
            self.full_dict = Conf.HUMANOID_FULL
            self.short_dict = Conf.HUMANOID_MOTION
            self.logger.info("Initializing Humanoid")
        elif robot_type == RobotType.SPIDER:
            com_port = Conf.SPIDER_PORT
            self.full_dict = self.short_dict = Conf.SPIDER_FULL
            self.logger.info("Initializing spider")
        else:
            self.logger.exception(
                f"{robot_type} is not a valid option for robot type"
            )
            self.main_logger.exception(
                f"Robot crashed -- '{robot_type}' is not a valid robot type"
            )
            raise ValueError(
                f"{robot_type} is not a valid option for robot type"
            )
        self.robot_type = robot_type
        self.active_auto_control = True
        self.full_control = False

        # Create serial port object for connection to the robot
        self.ser = serial.Serial(
            com_port,
            Conf.BAUDRATE,
            Conf.BYTESIZE,
            Conf.PARITY,
            timeout=Conf.SER_TIMEOUT
        )

        # Loop until serial connection made or connection times out
        duration = time.time() - self.start
        while not self.ser.isOpen():
            if duration > Conf.PORT_TIME_OUT:
                self.logger.exception("Serial port timed out")
                self.main_logger.exception(
                    "Robot crashed -- Serial port timed out"
                )
                raise Exception("Connection timed out")
            self.ser.Open()
            duration = time.time() - self.start
        self.logger.debug(
            f"Serial port connected after "
            f"{pretty_time(duration, is_raw=False)}"
        )
        self.logger.info(f"Robot init ran in {pretty_time(self.start)}")

    def send_command(self, motion_cmd):
        self.logger.debug("send_command called")
        if type(motion_cmd) == int:
            motion_cmd = self.get_hex_cmd(motion_cmd)
        if self.robot_type == RobotType.HUMAN:
            lock = Conf.HUMANOID_LOCK
        elif self.robot_type == RobotType.SPIDER:
            lock = Conf.SPIDER_LOCK

        with lock:
            try:
                self.sub_send_command(Conf.HEX_STOP)
                self.sub_send_command(Conf.HEX_RESET)
                self.logger.debug("motion command ", motion_cmd)
                self.sub_send_command(motion_cmd)
                self.sub_send_command(Conf.HEX_RESUME)
                self.ser.flush()
            except serial.SerialException as e:
                self.ser.flush()
                self.logger.exception(f"Serial exception hit: {e}")

    def sub_send_command(self, hex_cmd, cache_wait=0.05):
        self.logger.debug(
            f"sub_send_command: sending motion command: {hex_cmd}"
        )
        self.ser.write(hex_cmd)
        self.clear_cache(cache_wait)

    def clear_cache(self, wait):
        self.logger.debug(f"clearing cache: wait time {wait}sec")
        check = ""
        while check == "":
            check = self.ser.read()
        time.sleep(wait)

    def get_hex_cmd(self, motion_num):
        self.logger.debug(f"get_hex_cmd called. motion_num: {motion_num}")

        if motion_num in self.full_dict:
            return Conf.HEX_HUNDRED_NUM[motion_num]
        else:
            self.logger.info(f"Motion number {motion_num} not allowed")
            return Conf.HEX_STOP

    def control(self, command):
        self.logger.debug("control started")
        if command == Conf.CMD_FULL_CONTROL:
            self.full_control = not self.full_control
            self.logger.info(
                f"Full control Toggled: full_control = {self.full_control}"
            )
        elif command == Conf.CMD_REMOTE:
            self.logger.error("remote not implemented")
        elif command == Conf.CMD_CALIBRATE:
            self.logger.error("calibrate not implemented")
        elif command == Conf.CMD_CALIBRATE_STOP:
            self.logger.error("calibrate stop not implemented")
        elif command == Conf.CMD_DETECT_ON:
            self.active_auto_control = True
        elif command == Conf.CMD_DETECT_OFF:
            self.active_auto_control = False
        elif command == Conf.CMD_EXIT or command == Conf.CMD_EXIT:
            ExitControl.gen = True
            self.main_logger.info("Robot control exiting program")
            self.logger.info("Robot control exiting program")
        else:
            try:
                command = int(command)
            except ValueError:
                self.logger.info(f"{command} is an unknown command")

            if self.full_control:
                if command in self.full_dict:
                    self.send_command(command)
                else:
                    self.logger.info(
                        f"{command} is an unknown motion number"
                    )
            elif command in self.short_dict:
                self.send_command(command)
            else:
                self.logger.info(f"{command} is an unknown motion number")

    def close(self):
        self.logger.info(
            f"Robot is closing after running for {pretty_time(self.start)} "
        )


def manual_robot_control(robot_type):
    robot = Robot.get_inst(robot_type)
    while not ExitControl.gen:
        command = input("Enter a Command or motion number: ")
        robot.control(command)
    robot.close()


if __name__ == "__main__":
    # This section is to be used to test functions/methods of this file
    manual_robot_control(RobotType.SPIDER)

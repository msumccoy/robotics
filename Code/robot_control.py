"""
Kuwin Wyke
Midwestern State University
"""
import logging
import os
import time
import serial
import termios
is_rpi = False
if "raspberrypi" in os.uname():
    is_rpi = True
    from adafruit_servokit import ServoKit

import log_set_up
from config import Conf
from enums import RobotType
from misc import get_int, pretty_time
from variables import ExitControl


class Robot:
    # TODO: Go in Heart2Heart and see what feed back can be obtained from the
    #  robot
    _inst = {}
    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
    logger = logging.getLogger(Conf.LOG_ROBOT_NAME)

    @staticmethod
    def get_inst(robot_type, enable_auto=True):
        with Conf.LOCK_GEN:
            if robot_type not in Robot._inst:
                Robot._inst[robot_type] = Robot(robot_type, enable_auto)
        return Robot._inst[robot_type]

    def __init__(self, robot_type, enable_auto):
        self.main_logger.info(f"Robot: started on version {Conf.VERSION}")
        self.logger.info(
            f"Robot started on version {Conf.VERSION}:\n"
            f"- robot_type: {robot_type}"
        )
        self.start = time.time()
        if robot_type == RobotType.HUMAN:
            com_port = Conf.HUMANOID_PORT
            self.full_dict = Conf.HUMANOID_FULL
            self.short_dict = Conf.HUMANOID_MOTION
            self.lock = Conf.LOCK_HUMANOID
            self.logger.info("Initializing Humanoid")
        elif robot_type == RobotType.SPIDER:
            com_port = Conf.SPIDER_PORT
            self.full_dict = self.short_dict = Conf.SPIDER_FULL
            self.lock = Conf.LOCK_SPIDER
            self.logger.info("Initializing spider")
        else:
            self.logger.exception(
                f"{robot_type} is not a valid option for robot type"
            )
            self.main_logger.exception(
                f"Robot: crashed -- '{robot_type}' is not a valid robot type"
            )
            raise ValueError(
                f"{robot_type} is not a valid option for robot type"
            )
        self.robot_type = robot_type
        self.active_auto_control = enable_auto
        self.full_control = False

        # Create serial port object for connection to the robot
        try:
            self.ser = serial.Serial(
                com_port,
                Conf.BAUDRATE,
                Conf.BYTESIZE,
                Conf.PARITY,
                timeout=Conf.SER_TIMEOUT
            )
        except serial.serialutil.SerialException:
            self.ser = None
            self.logger.exception(
                "Robot control failed. Cannot connect to robot!!!!!!!!!!!!!!!"
            )
        # 90 degrees is the center position
        self.servo_posLR = self.servo_posUD = 90
        self.head_delta_theta = 5
        if is_rpi:
            self.servos = ServoKit(channels=16)
            self.servos.servo[0].angle = self.servo_posLR  # Left and Right
            self.servos.servo[1].angle = self.servo_posUD  # Up and Down
        else:
            self.servos = None
        time.sleep(3)
        self.send_command(-1)
        self.debug_info = ""
        self.logger.info(f"Robot init ran in {pretty_time(self.start)}")

    def send_command(self, motion_cmd, auto=False):
        self.debug_info = f"send_command: motion_cmd = {motion_cmd}\n"  ######
        if self.ser is None:
            if auto and not self.active_auto_control:
                self.logger.debug(
                    "Auto command sent but auto control off and no connection"
                    f". motion_cmd = {motion_cmd}"
                )
                return False
            self.logger.debug(
                "send_command: no robot to connect to. "
                f"motion_cmd = {motion_cmd}"
            )
            self.debug_info += (  ############################################
                f"no robot to connect to. \n"  ###############################
            )  ###############################################################
            print(  # delete #################################################
                "send_command: no robot to connect to."  #####################
                f"motion_cmd={motion_cmd}"  ##################################
            )  ###############################################################
            return False
        # Need to make sure robot is aware that command is being sent before
        # sending command
        self.logger.debug(f"send_command called: command -- {motion_cmd}")
        if auto and not self.active_auto_control:
            self.logger.debug("Auto command sent but auto control off")
            return False
        if (
                motion_cmd == Conf.CMD_STOP or motion_cmd == Conf.CMD_STOP1
                or type(motion_cmd) == int and motion_cmd < 0
        ):
            if self.robot_type == RobotType.HUMAN:
                motion_cmd = self.get_hex_cmd(1)
            elif self.robot_type == RobotType.SPIDER:
                motion_cmd = self.get_hex_cmd(17)
        elif motion_cmd == Conf.CMD_FORWARD or motion_cmd == Conf.CMD_FORWARD1:
            if self.robot_type == RobotType.HUMAN:
                motion_cmd = self.get_hex_cmd(15)
            elif self.robot_type == RobotType.SPIDER:
                motion_cmd = self.get_hex_cmd(5)
        elif motion_cmd == Conf.CMD_BACKWARD or motion_cmd == Conf.CMD_BACKWARD1:
            if self.robot_type == RobotType.HUMAN:
                motion_cmd = self.get_hex_cmd(16)
            elif self.robot_type == RobotType.SPIDER:
                motion_cmd = self.get_hex_cmd(6)
        elif motion_cmd == Conf.CMD_LEFT or motion_cmd == Conf.CMD_LEFT1:
            if self.robot_type == RobotType.HUMAN:
                motion_cmd = self.get_hex_cmd(19)
            elif self.robot_type == RobotType.SPIDER:
                motion_cmd = self.get_hex_cmd(13)
        elif motion_cmd == Conf.CMD_RIGHT or motion_cmd == Conf.CMD_RIGHT1:
            if self.robot_type == RobotType.HUMAN:
                motion_cmd = self.get_hex_cmd(20)
            elif self.robot_type == RobotType.SPIDER:
                motion_cmd = self.get_hex_cmd(12)
        elif motion_cmd == Conf.CMD_DANCE or motion_cmd == Conf.CMD_DANCE1:
            if self.robot_type == RobotType.HUMAN:
                motion_cmd = self.get_hex_cmd(7)
            elif self.robot_type == RobotType.SPIDER:
                motion_cmd = self.get_hex_cmd(16)
        elif motion_cmd == Conf.CMD_KICK or motion_cmd == Conf.CMD_KICK1:
            if self.robot_type == RobotType.HUMAN:
                motion_cmd = self.get_hex_cmd(25)
            elif self.robot_type == RobotType.SPIDER:
                motion_cmd = self.get_hex_cmd(9)
        elif type(motion_cmd) == int:
            motion_cmd = self.get_hex_cmd(motion_cmd)

        with self.lock:
            try:
                self.sub_send_command(Conf.HEX_STOP)
                self.sub_send_command(Conf.HEX_RESET)
                self.logger.debug(f"motion command {motion_cmd}")
                self.sub_send_command(motion_cmd)
                self.sub_send_command(Conf.HEX_RESUME)
                self.ser.flush()
            except serial.SerialException as e:
                try:
                    self.logger.exception(f"Serial exception hit: {e}")
                    self.ser.flush()
                except termios.error:
                    self.main_logger.exception(
                        "Robot Unable to connect. Please check configuration"
                    )
                    self.logger.exception(
                        "Robot Unable to connect. Please check configuration"
                    )
                self.ser = None
        return True

    def sub_send_command(self, hex_cmd, cache_wait=0.05):
        self.logger.debug(
            f"sub_send_command: sending motion command -- {hex_cmd}"
        )
        self.ser.write(hex_cmd)
        self.clear_cache(cache_wait)

    def clear_cache(self, wait):
        self.logger.debug(f"clearing cache: wait time {wait}sec")
        check = ""
        while check == "":
            check = self.ser.read(4)
        if check == Conf.HEX_ACK_COMMAND:
            self.logger.debug(f"GOOD: Check is the same as ack -- {check}")
        else:
            self.logger.debug(f"BAD: Check wrong -- {check}")
        time.sleep(wait)

    def get_hex_cmd(self, motion_num):
        self.logger.debug(f"get_hex_cmd called. motion_num: {motion_num}")

        if motion_num in self.full_dict:
            return Conf.HEX_HUNDRED_NUM[motion_num]
        else:
            self.logger.info(f"Motion number {motion_num} not allowed")
            return Conf.HEX_STOP

    def send_head_command(self, motion_cmd, pos=None, auto=False):
        if is_rpi:
            if auto and not self.active_auto_control:
                self.logger.debug(
                    "send_head_command: auto head control attempted but"
                    " active_auto_control off"
                )
                return False
            if motion_cmd == Conf.CMD_RH_UP:
                self.servo_posUD += self.head_delta_theta
            elif motion_cmd == Conf.CMD_RH_DOWN:
                self.servo_posUD -= self.head_delta_theta
            elif motion_cmd == Conf.CMD_RH_LEFT:
                self.servo_posLR += self.head_delta_theta
            elif motion_cmd == Conf.CMD_RH_RIGHT:
                self.servo_posLR -= self.head_delta_theta
            elif motion_cmd == Conf.ROBOT_HEAD_SET_U_D and pos is not None:
                self.servo_posUD = pos
            elif motion_cmd == Conf.ROBOT_HEAD_SET_L_R and pos is not None:
                self.servo_posLR = pos
                pass
            self.set_head()
        else:
            self.logger.info(
                "Cannot control head servos as this program is not being "
                "executed on a raspberry pi"
            )

    def set_head(self):
        if self.servo_posLR < Conf.RBT_MIN_HEAD_RIGHT:
            self.servo_posLR = Conf.RBT_MIN_HEAD_RIGHT
        elif self.servo_posLR > Conf.RBT_MAX_HEAD_LEFT:
            self.servo_posLR = Conf.RBT_MAX_HEAD_LEFT

        if self.servo_posUD < Conf.RBT_MIN_HEAD_FORWARD:
            self.servo_posUD = Conf.RBT_MIN_HEAD_FORWARD
        elif self.servo_posUD > Conf.RBT_MAX_HEAD_BACK:
            self.servo_posUD = Conf.RBT_MAX_HEAD_BACK

        self.servos.servo[0].angle = self.servo_posLR  # Left and Right
        self.servos.servo[1].angle = self.servo_posUD  # Up and Down

    ##########################################################################
    # Manual control for robot ###############################################
    ##########################################################################
    def manual_control(self):
        self.logger.debug("control started")
        while ExitControl.gen and ExitControl.robot:
            if self.full_control:
                print("FULL CONTROL ACTIVE!!!!!!!!! BE CAREFUL!!!!!!!!")
            command = input("Enter a Command or motion number: ")
            if command == Conf.CMD_FULL_CONTROL:
                self.full_control = not self.full_control
                self.logger.debug(
                    f"Full control Toggled: full_control={self.full_control}"
                )
            elif command == Conf.CMD_AUTO_ON:
                self.active_auto_control = True
                self.logger.debug("Enabling auto control")
            elif command == Conf.CMD_AUTO_OFF:
                self.active_auto_control = False
                self.logger.debug("Disabling auto control")
            elif command == Conf.CMD_EXIT or command == Conf.CMD_EXIT1:
                ExitControl.gen = False
                self.main_logger.info("Robot: control exiting program")
                self.logger.info("Robot control exiting program")
            elif command == Conf.CMD_STOP or command == Conf.CMD_STOP1:
                self.active_auto_control = False
                self.send_command(Conf.CMD_STOP)
                self.logger.debug(
                    "Turning off auto control and stopping robot"
                )
            elif command == Conf.CMD_FORWARD or command == Conf.CMD_FORWARD1:
                self.send_command(Conf.CMD_FORWARD)
            elif command == Conf.CMD_BACKWARD or command == Conf.CMD_BACKWARD1:
                self.send_command(Conf.CMD_BACKWARD)
            elif command == Conf.CMD_LEFT or command == Conf.CMD_LEFT1:
                self.send_command(Conf.CMD_LEFT)
            elif command == Conf.CMD_RIGHT or command == Conf.CMD_RIGHT1:
                self.send_command(Conf.CMD_RIGHT)
            elif command == Conf.CMD_DANCE or command == Conf.CMD_DANCE1:
                self.send_command(command)
            elif command == Conf.CMD_KICK:
                self.send_command(Conf.CMD_KICK)
            else:
                try:
                    command = int(command)
                except ValueError:
                    pass
                if self.full_control:
                    if command in self.full_dict:
                        self.send_command(command)
                    elif type(command) == int and command < 0:
                        self.send_command(command)
                    else:
                        self.logger.info(
                            f"{command} is an unknown motion number"
                        )
                elif command in self.short_dict:
                    self.send_command(command)
                elif type(command) == int and command < 0:
                    self.send_command(command)
                else:
                    self.logger.info(f"{command} is an unknown motion number")

    ##########################################################################

    def close(self):
        self.main_logger.info(
            f"Robot: is closing after running for {pretty_time(self.start)}"
        )
        self.logger.info(
            f"Robot: is closing after running for {pretty_time(self.start)}\n"
        )
        ExitControl.robot = False


def main():
    robot = Robot.get_inst(RobotType.SPIDER)
    robot.manual_control()
    robot.close()


if __name__ == "__main__":
    # This section is to be used to test functions/methods of this file
    main()

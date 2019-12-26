""" Kuwin Wyke
Midwestern State University
Start: 6 November 2019
End: work in progress

This module is designed to be used in the ball recognition program in the
folder named "ball_recognition_v1". It contains a class to connect to the
robot, a function to control the robot through object detection and a function
to control the robot manually.


Classes:


Functions:


"""

import time

# Project specific modules
import variables
from debug import debug_robot

if variables.test_environment:
    from test_environment import serial
else:
    import serial


# Create class to handle robot object
class Robot:
    """ Currently this class is a place holder. Once completed this class
    will be used to create the connection with the robot.

    Additionally this class will have several actions that the robot can take.
    Primarily it will have built in actions and a function to create motion
    commands to send to the robot.

    Function:
    generate_motion_cmd -- used to create motion command
    """

    def __init__(self):
        # Create serial port object for connection to the robot
        self.ser = serial.Serial(variables.com_port, 115200, serial.EIGHTBITS,
                                 serial.PARITY_EVEN, serial.STOPBITS_ONE,
                                 timeout=1)
        start_time = time.time()
        # Loop until serial connection made or connection times out
        while not self.ser.isOpen():
            self.ser.Open()
            if (not self.ser.isOpen() and
                    (time.time() - start_time)
                    > variables.serial_port_time_out):
                raise Exception("Connection timed out")
        if debug_robot:
            print("The connection took ", time.time() - start_time, "seconds")


    def automatic_control(self):
        """ This function is to be used to send commands to the robot."""
        # Create robot object to initiate connection with the robot

        # Set to default state
        motion_num = -1
        while 1:
            with variables.lock:
                if variables.exit_gen or variables.exit_auto:
                    break
                if variables.thread_motion_num != -1:
                    motion_num = variables.thread_motion_num
            if motion_num != -1:
                self.send_motion_cmd(motion_num)
                print("send complete")
                motion_num = -1
                with variables.lock:
                    variables.thread_motion_num = -1

    def send_motion_cmd(self, motion_number):
        """ This function sends the command to the robot unless the delay is
        still active.
        """
        if motion_number == "stop":
            motion_number = 1  # Set to home position
        # self.ser.write(variables.stop_motion)
        motion_cmd = self.generate_motion_cmd(motion_number)
        self.ser.write(motion_cmd)
        return motion_cmd

    def generate_motion_cmd(self, motion_number):
        """ This function generates a motion command hex string to send to
        the robot.

        Motion command string consist of seven 2 digit hex numbers
        position 0: "07" represents a 7 bytes
        position 1: "0c" represents motion command in Heart2Heart
        position 2: "80" not sure...
        position 3: variable. Lower byte of motion number
        position 4: variable. Higher byte of motion number
        position 5: "00" not sure...
        position 6: variable. Check sum
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

    def clear_cache(self):
        """ This function clears the cache on the raspberry pi and makes sure
        the robot responded with the ok response
        """
        check = ""
        start_time = time.time()
        # Try to get response from cache until retrieved or timed out
        while check == "":
            check = self.ser.read()
            # print("clear_cache check: ", check)
            # Check for timeout
            if (check == "" and
                    (time.time() - start_time)
                    > variables.connection_time_out):
                raise Exception("Connection port time out")
        # If the wrong response is retrieved exit and print response
        # print("Response: ", check)

    def action(self, motion_number):
        """ Dummy action

        This function is just to prove that action can be taken. Once
        the code is complete an actual action will be created.
        """
        start = time.time()
        motion_cmd = self.generate_motion_cmd(motion_number)
        self.send_motion_cmd(motion_number)
        duration = time.time() - start
        print("action called")

    def __del__(self):
        self.ser.close()

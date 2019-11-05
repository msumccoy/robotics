""" Kuwin Wyke
Midwestern State University
Start: 10 October 2019
End: work in progress

This program detects a ball by using a filter that looks only for the color
of the ball. There is a function to manually calibrate the filter. Once only
the color of the ball is detected as input, the program looks for a circle
using a built in OpenCV function. There is also a function to draw the
detected circle and a box around the circle. The box is drawn to demonstrate
the ability to make a ROI (region of interest) to use later when implementing
Haar cascades.

Programed on windows
tested on windows 10 and raspberry pi (debian jessie).
both: python 3
raspberry pi: opencv version 4.0.0
windows: opencv version 4.1.1
"""

import cv2
import numpy as np
import time
import threading
import queue
import platform

# Import custom modules
# noinspection PyUnresolvedReferences
import ball_recognition_variables as variables

# Check if running on rasp pi to import pi cam modules
if platform.system() != "Windows":
    import serial
    from picamera.array import PiRGBArray
    from picamera import PiCamera
else:
    # Dummy code to handle lack of serial class on windows pc
    class dummy_robot:
        """ This class will be used just to mimic the wait times associated
        with operating the real robot.
        """
        def decode(self, hex_string):
            """ This function decodes hex strings and checks the length and
            the check sum. Later functionality to check command type will be
            added.
            """
            # hex_string = "-1" + hex_string
            hex_string_array = hex_string[2:].split(r"\x")
            if len(hex_string_array) == int(hex_string_array[0], 16):
                print("Legnth good")
            sum = 0
            for index in range(len(hex_string_array)):
                if index != len(hex_string_array) - 1:
                    try:
                        sum += int(hex_string_array[index], 16)
                    except:
                        print("Hex to decimal fail")
            # Convert sum to hex and truncate to only the last two digits
            sum = hex(sum)[-2:]
            if sum == hex_string_array[-1]:
                print("Check sum good")
            time.sleep(5)
            print(hex_string)

    dummy = dummy_robot()

    class serial:
        global dummy
        EIGHTBITS = None
        PARITY_EVEN = None
        STOPBITS_ONE = None

        class Serial:
            def __init__(self, *args, **kwargs):
                pass
            count = 0
            count2 = 0

            def Open(self):
                pass

            def isOpen(self):
                self.count += 1
                if self.count > 1000:
                    return variables.ok_response

            def close(self):
                # print("serial close")
                pass

            def read(self):
                # print("serial read")
                # self.count2 += 1
                return variables.ok_response

            def write(self, hex_string=""):
                # print("serial write : ", hex_string)
                dummy.decode(hex_string)

# A complete description of each class and function can be found in the
# relevant class or function.
""" Classes: 
Robot() -- used to control interface with robot
Camera() -- used to control camera interface

Functions:
draw_circles -- used to draw detected circles on the image
get_filtered_image -- used to create the filtered image for circle detection
calibrate_filter -- used to calibrate filter to account for change in 
                    lighting conditions.
vision_control -- used to do object recognition and then sent action to 
                  robot.
"""


def main():
    """
    """
    robot = Robot()
    robot_thread = threading.Thread(target=robot_control, args=(robot,))
    manual_robot_thread = threading.Thread(target=robot.manual_control)
    object_detector_thread = threading.Thread(target=object_detection)
    robot_thread.start()
    object_detector_thread.start()
    object_detector_thread.join()
    with variables.lock:
        variables.exit_code = 1
    # variables.exit = input(" enter")


# Create class to handle camera object
class Camera:
    """ This class is used to create a camera object. With this class
    both windows and raspberry pi will be able to use the same object because
    this class will handle the differences between the two operating systems.

    Additionally it will reduce code when implementing camera operations in
    different functions.
    """

    # Initialize the class. No variables are required because the only
    # condition is the operating system.
    def __init__(self):
        # Check if the operating system is linux, (raspberry pi will return
        # ("Linux"). The raspberry pi uses a pi cam and therefore needs
        # the pi cam implementation of the camera.
        if platform.system() == "Linux":
            # print("starting camera") #for debugging#########################
            self.cam = PiCamera()
            self.cam.resolution = (variables.set_width, variables.set_height)
            self.raw_capture = PiRGBArray(self.cam)
        else:
            # print("starting camera") #for debugging#########################
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, variables.set_width)
            self.cap.set(4, variables.set_height)
        self.get_frame()
        # Get the actual width and height that was set.
        self.height, self.width, self.channels = self.frame.shape

    def get_frame(self):
        """ This function gets the current image in front of the camera"""
        if platform.system() == "Linux":
            self.cam.capture(self.raw_capture, "bgr", True)
            self.frame = self.raw_capture.array
            self.raw_capture.truncate(0)
        else:
            _, self.frame = self.cap.read()

    # Create the destructor to close the camera connections.
    def __del__(self):
        if platform.system() == "Linux":
            self.cam.close()
        else:
            self.cap.release()


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
        # Create serial port object
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

    def manual_control(self):
        # This module is used to manually control the robot
        print("Starting manual control")
        exit_control = True
        # Continue until exit command requested
        while exit_control:
            motion_num = input("Enter motion number \n")
            # Give access to full range of motions
            if motion_num == "full control":
                print("full control")
                motion_num = input("Enter motion number \n")
                # Print motion numbers and their corresponding actions
                if motion_num == "dict":
                    for key in variables.full_motion_dictionary:
                        print(key, " : ",
                              variables.full_motion_dictionary[key])
                    motion_num = input("Enter motion number \n")
                # Catch in case non int entered
                try:
                    motion_num = int(motion_num)
                except Exception as e:
                    print(e)
                    print("full control failed")
                # Only excecute command if it is valid
                if motion_num in variables.full_motion_dictionary:
                    print(motion_num, " in hex ",
                          self.send_motion_cmd(motion_num))
                continue

            if motion_num == "exit":
                exit_control = False
            if motion_num == "dict":
                for key in variables.motion_dictionary:
                    print(key, " : ",
                          variables.full_motion_dictionary[key])
                continue
            if motion_num == "stop":
                print(motion_num, " in hex ",
                      self.send_motion_cmd(motion_num))
            try:
                motion_num = int(motion_num)
            except Exception as e:
                print(e)
            if motion_num in variables.motion_dictionary:
                print(motion_num, " in hex ",
                      self.send_motion_cmd(motion_num))
            else:
                print("not valid")

    def send_motion_cmd(self, motion_number):
        """ This function sends the command to the robot unless the delay is
        still active.
        """
        if motion_number == "stop":
            motion_number = 1  # Set to home position
        # self.ser.write(variables.stop_motion)
        self.clear_cache()
        # self.ser.write(variables.reset_counter)
        self.clear_cache()
        motion_cmd = self.generate_motion_cmd(motion_number)
        self.ser.write( motion_cmd)

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
        motion_cmd =self.generate_motion_cmd(motion_number)
        self.send_motion_cmd(motion_number)
        duration = time.time() - start
        print("action called")

    def __del__(self):
        self.ser.close()


def robot_control(robot=Robot()):
    """ This function is to be used to send commands to the robot."""
    # Create robot object to initiate connection with the robot

    # Set to default state
    motion_num = -1
    while 1:
        with variables.lock:
            if variables.exit_code:
                break
            if variables.thread_motion_num != -1:
                motion_num = variables.thread_motion_num
                variables.thread_motion_num = -1
        if motion_num != -1:
            robot.send_motion_cmd(motion_num)
            motion_num = -1




def object_detection():
    """ input: none
    Process: Get filter variables from file. Get frames from camera
    continuously. Detect circles in each frame and draw circles along with
    bounding boxes. output image continuously. send a message to robot to
    perform action

    output:
    -1 for fail
    0 for success

    This function is incomplete at the moment.
    """


    # Create camera object
    camera = Camera()
    # time1 = time.time()  # for debugging group 2############################
    # cycles = 0  # for debugging group 2#####################################
    # Create infinite loop for camera frames
    while 1:
        # Calculate average frame processing time
        # cycles += 1  # for debugging group 2################################
        # total_time = time.time() - time1  # for debugging group 2###########
        # average = total_time / cycles  # for debugging group 2##############
        # print("Total = ", total_time)  # for debugging group 2##############
        # print("Average = ", average)  # for debugging group 2###############

        # Refresh frame
        camera.get_frame()

        # Get filtered image for processing
        _, filtered_image_gray = (
            get_filtered_image(camera.frame, variables.lower_range,
                               variables.upper_range))

        # Detect circles in filtered image but use try except to prevent
        # program from crashing when circles are not found
        try:
            circles = cv2.HoughCircles(filtered_image_gray,
                                       cv2.HOUGH_GRADIENT, 1, 50,
                                       param1=variables.circle_detect_param,
                                       param2=variables.circle_detect_param2,
                                       minRadius=0, maxRadius=0)
            # Draw circles for visual representation of detection
            circles = np.uint16(np.around(circles))
            num_circles = draw_circles(camera.frame, circles, camera.width,
                                       camera.height)
            # If object detected send message to robot control
            if num_circles == 1:
                with variables.lock:
                    variables.thread_motion_num = 1
        except Exception as e:
            # print(e) # for debugging #######################################
            pass

        # Show full image with detected circles and filter
        cv2.imshow("Full image", camera.frame)

        k = cv2.waitKey(5) & 0xFF
        # End if user presses any key. 255 is the default value for windows.
        # -1 is the default on the raspberry pi. Save image if s is pressed
        if k == ord("s"):
            cv2.imwrite("full_image.jpg", camera.frame)
        if k != 255 and k != -1:
            break
    cv2.destroyAllWindows()
    # Return 0 to report success
    return 0


# Create function to draw circles
def draw_circles(image, circles, width, height, max_circles=60, buffer=5):
    """
    Input: image - opencv compatible array (current frame)
    circle - output from cv2.HoughCircles
    width, height - width and height of image
    max_circles - limit the number of detected circles for testing
    buffer - used to increase the size of the box around the circle.

    proccess: draw all the circles detected using cv2.HoughCircles and a
    box around all the circles.

    output: number of circles
    """
    # Count the number of circles to prevent the system from getting
    # bogged down trying to draw too many circles
    num_circles = 0
    for i in circles[0, :]:
        num_circles += 1
    if num_circles <= max_circles:
        for i in circles[0, :]:
            # Get coordinates for top and bottom of the box
            top_left_x = i[0] - i[2] - buffer
            top_left_y = i[1] - i[2] - buffer
            bottom_right_x = i[0] + i[2] + buffer
            bottom_right_y = i[1] + i[2] + buffer
            # Make sure the top is within range
            if top_left_x < 0:
                top_left_x = 1
            if top_left_x > width:
                top_left_x = 1
            if top_left_y > height:
                top_left_y = 1
            if top_left_y < 0:
                 top_left_y = 1
            # Draw the box
            cv2.rectangle(image, (top_left_x, top_left_y),
                          (bottom_right_x, bottom_right_y),
                          (0, 0, 0), 0)
            # draw the outer circle
            cv2.circle(image, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(image, (i[0], i[1]), 2, (0, 0, 255), 3)
        return num_circles
    else:
        # print("error too many circles  ", num_circles) # For debugging######
        # Return error code
        return -1


# Create function to filter image. Then return the filtered image
def get_filtered_image(image, lower_range, upper_range):
    """
    Input:  image - camera frame
            lower_range - lower hsv range (array of 3 numbers)
            upper_range - upper hsv range (array of 3 numbers)

    Process: take image and remove all colors out side of color range to
    create a mask. This mask is then used to create a filtered image.

    output: colored filtered image and gray filtered image.
    """
    # Create filter
    # Get hsv color scheme
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Threshold the hsv color scheme to get only desired colors
    mask = cv2.inRange(hsv, lower_range, upper_range)

    # Use bitwise and to find only regions of the original picture that
    # match the color you are looking for
    filtered_image = cv2.bitwise_and(image, image,
                                     mask=mask)

    # Convert filtered image to gray scale. Image cannot be converted to
    # gray scale immediately. Convert anything but hsv to BRG first.
    filtered_image = cv2.medianBlur(filtered_image, 3)
    filtered_image_gray = cv2.cvtColor(filtered_image, cv2.COLOR_HLS2BGR)
    filtered_image_gray = cv2.cvtColor(filtered_image_gray,
                                       cv2.COLOR_BGR2GRAY)
    # Return colored filtered image for human consumption and gray filtered
    # image for processing.
    return [filtered_image, filtered_image_gray]


# Create function to calibrate filter
def calibrate_filter():
    """ input: none
    Process: Get previously stored variables from from. Create track bars that
    are used to adjust the various parameters. Continuously capture frames
    from the camera and detect circles in each frame. Then draw detected
    circles
    output: none

    This module is used to fine tune the variables for filtering for
    the color of the ball and tuning the variables for ball detection.
    """

    # Create function to save adjusted parameters
    def file_save():
        print("saving")
        string = str(variables.lower_limit) + '\n'
        string += str(variables.lower_limit2) + '\n'
        string += str(variables.lower_limit_hue) + '\n'
        string += str(variables.upper_limit) + '\n'
        string += str(variables.upper_limit2) + '\n'
        string += str(variables.upper_limit_hue) + '\n'
        string += str(variables.circle_detect_param) + '\n'
        string += str(variables.circle_detect_param2)
        variable_string = open(variables.variables_file, "w")
        variable_string.write(string)
        variable_string.close()

    # Create functions to change parameters of hsv filter
    def lower_change(pos):
        variables.lower_limit = pos

    def lower_change2(pos):
        variables.lower_limit2 = pos

    def lower_change3(pos):
        variables.lower_limit_hue = pos

    def upper_change(pos):
        variables.upper_limit = pos

    def upper_change2(pos):
        variables.upper_limit2 = pos

    def upper_change3(pos):
        variables.upper_limit_hue = pos

    # Create functions to change circle detection parameters
    def circle_detect_change(pos):
        variables.circle_detect_param = pos

    def circle_detect_change2(pos):
        variables.circle_detect_param2 = pos

    # Create variable for track bar names to make it easy to change
    filter_bars = "filter_bars"
    # Create second windows name to accommodate all bars
    circle_bars = "circle_bars"
    # Create named window to put track bars
    cv2.namedWindow(filter_bars)
    cv2.namedWindow(circle_bars)

    # Create Track bars to adjust filter and circle detection parameters
    cv2.createTrackbar("Lower bottom", filter_bars, variables.lower_limit,
                       360, lower_change)
    cv2.createTrackbar("Lower top", filter_bars, variables.lower_limit2, 360,
                       lower_change2)
    cv2.createTrackbar("lower hue", filter_bars, variables.lower_limit_hue,
                       360, lower_change3)
    cv2.createTrackbar("upper bottom", filter_bars, variables.upper_limit,
                       360, upper_change)
    cv2.createTrackbar("upper top", filter_bars, variables.upper_limit2, 360,
                       upper_change2)
    cv2.createTrackbar("upper hue", filter_bars, variables.upper_limit_hue,
                       360, upper_change3)
    cv2.createTrackbar("circle param", circle_bars,
                       variables.circle_detect_param, 500,
                       circle_detect_change)
    cv2.createTrackbar("circle param 2", circle_bars,
                       variables.circle_detect_param2,
                       500, circle_detect_change2)

    camera = Camera()
    # time1 = time.time()  # for debugging group 1############################
    # cycles = 0  # for debugging group 1#####################################
    # Create infinite loop for camera frames
    while 1:
        # Calculate average frame processing time
        # cycles += 1  # for debugging group 1################################
        # total_time = time.time() - time1  # for debugging group 1###########
        # average = total_time / cycles  # for debugging group 1##############
        # print("Total = ", total_time)  # for debugging group 1##############
        # print("Average = ", average)  # for debugging group 1###############

        # Create arrays for filter parameters
        variables.lower_range = np.array([variables.lower_limit_hue,
                                          variables.lower_limit,
                                          variables.lower_limit2])
        variables.upper_range = np.array([variables.upper_limit_hue,
                                          variables.upper_limit,
                                          variables.upper_limit2])

        # Refresh frame
        camera.get_frame()
        # Get filtered image for processing
        filtered_image, filtered_image_gray = (
            get_filtered_image(camera.frame, variables.lower_range,
                               variables.upper_range))

        # Detect circles in filtered image but use try except to prevent
        # program from crashing when circles are not found
        try:
            circles = cv2.HoughCircles(filtered_image_gray,
                                       cv2.HOUGH_GRADIENT,
                                       1, 50,
                                       param1=variables.circle_detect_param,
                                       param2=variables.circle_detect_param2,
                                       minRadius=0, maxRadius=0)
            # Draw circles for visual representation of detection
            circles = np.uint16(np.around(circles))
            draw_circles(camera.frame, circles, camera.width, camera.height)
        except Exception as e:
            # print(e)  # for debugging ######################################
            pass

        # Show full image with detected circles and filter
        cv2.imshow("Full image", camera.frame)
        cv2.imshow("filter", filtered_image)

        # Check to see if user is done adjusting filter. End if user is done.
        k = cv2.waitKey(5) & 0xFF
        # Check to see if user does not want to save changes
        if k == ord("x"):
            print("not saving")
            break
        # Check to see if user wants to save a picture of full or full and
        # the filter
        elif k == ord("1"):
            cv2.imwrite("Full image.jpg", camera.frame)
            file_save()
            break
        elif k == ord("2"):
            cv2.imwrite("Full image.jpg", camera.frame)
            cv2.imwrite("filter.jpg", filtered_image)
            file_save()
            break
        # End if user presses any other key. 255 is the default value for
        # windows. -1 is the default on the raspberry pi
        elif k != 255 and k != -1:
            file_save()
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()


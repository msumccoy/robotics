import threading
import cv2
import serial
import time
import sys
import numpy as np

# Project specific modules
import variables
import debug
from camera import Camera


reset_status = "\x11\x00\x02\x02\x00\x00\x4b\x04\x00\x00\x00\x00\x00\x00\x00\x00\x64"
stop_motion = "\x09\x00\x02\x00\x00\x00\x10\x83\x9e"
resume_motion = "\x09\x00\x02\x00\x00\x00\x13\x83\xa1"

# create and open a serial port
ser = serial.Serial("/dev/rfcomm2", 115200, serial.EIGHTBITS,
                    serial.PARITY_EVEN, serial.STOPBITS_ONE, timeout = 1)

while ser.isOpen() == False:
    ser.Open()

time.sleep(0.05)

def main():
    detect = ObjectDetection()

    print("Initializing humanoid", stop_motion)
    ser.write(stop_motion)
    time.sleep(1)
    a = ""
    while a == "":
        a = ser.read(4)
        print("clearing cache")
    time.sleep(0.05)

    play_motion(int(input("Enter a motion number: ")), 1)

    # while a == "":
    #     a = ser.read(4)
    #     print("clearing cache")
    # time.sleep(0.05)
    #
    # detect.calibrate_filter()
    # motion = int(detect.object_detection())
    # play_motion(motion)

    ser.flush()
    time.sleep(1)
    ser.close()
    time.sleep(1)
    sys.exit()


def int_to_hex_str(num_int):
    """Return an integer converted to hex"""
    num_conv = (int(
        num_int) * 8) + 11  # convert integer number; multiply by 8, start at 11
    num_hex = hex(num_conv)[
              2:]  # convert number from int to hex, slice "0x" prefix

    if not ((len(num_hex) % 2) == 0):
        num_hex = "0" + num_hex  # if length is not even, prefix with a 0 to make length even

    if ((len(num_hex) >= 4) == 0):
        num_hex = "00" + num_hex  # if length is not 4 or more, prefix with 00

    # alternate method to ensure minimum length of 4 using zero as padding
    # hex_num.zfill(4)

    return num_hex  # return hex value representing the original integer

def make_motion_cmd(motion_num):
    """Return a hex motion command"""
    cmd_buffer = [None] * 7  # create empty command with length of 7 bytes
    cmd_buffer[0] = "07"  # store command length (7 = 7 bytes)
    cmd_buffer[1] = "0c"  # store command type (c = motion)
    cmd_buffer[2] = "80"  # store 80

    num_hex = int_to_hex_str(
        motion_num)  # convert motion number from integer to hex

    cmd_buffer[3] = num_hex[-2:]  # store the last two hex values (low byte)
    cmd_buffer[4] = num_hex[
                    -4:-2]  # store the two hex values before the last two (high byte)

    cmd_buffer[5] = "00"  # store null

    checksum = 0  # create empty checksum

    for i in range(6):
        checksum += int(cmd_buffer[i],
                        16)  # convert hex bytes to int, sum each with previous checksum result

    cmd_buffer[6] = str(
        hex(checksum)[-2:])  # store the low byte of the final hex checksum
    cmd_hex_str = ""  # create empty placeholder for final command

    for i in range(7):
        cmd_hex_str += (r'\x' + cmd_buffer[i])  # merge hex bytes to one command string

    cmd_hex_str = cmd_hex_str.decode(
        'string_escape')  # remove extra backslash from escape characters
    return cmd_hex_str  # return hex command string


def play_motion(motion_num, sleep_wait=0.5):
    try:
        # write array for Stop Motion
        print("Stopping Motion", stop_motion)
        ser.write(stop_motion)
        a = ""
        while a == "":
            a = ser.read(4)
        print(a)
        print(a.encode("hex"))
        time.sleep(0.05)

        # write array for Reset Program Counter
        print("Reseting Program Counter", reset_status)  # debugging
        ser.write(reset_status)
        a = ""
        while a == "":
            a = ser.read(4)
        print(a)  # debugging
        print(a.encode("hex"))
        time.sleep(0.05)

        # prepare motion command
        motion_cmd_str = make_motion_cmd(motion_num)
        print("motion number: ", motion_num)  # debugging
        print("Set Motion", repr(motion_cmd_str))  # debugging

        # write array for Set Motion
        ser.write(motion_cmd_str)
        a = ""
        while a == "":
            a = ser.read(4)
        print(a.encode("hex"))

        # write array to run the motion
        print("Running the Motion %s\n", resume_motion)
        ser.write(resume_motion)
        a = ""
        while a == "":
            a = ser.read(4)
        print(a.encode("hex"))

        # clear buffer
        ser.flush()

    except serial.SerialException:
        # clear buffer
        ser.flush()
        ser.close()
        sys.exit()

    print("Sleeping", sleep_wait)
    time.sleep(sleep_wait)

    print("Done.")
#################################################################################################
class ObjectDetection:
    # Create camera object
    camera = Camera()

    # Create circle detection code
    def object_detection(self):
        """Process:
        * Get filter variables from file.
        * Get frames from camera continuously.
        * Filter frames for selective color
        * Detect circles in each filtered image
        * Draw circles along with bounding boxes around detectd circles.
        * Output image continuously.
        * send a message to robot to perform action

        :return:
        * -1 for fail
        * 0 for success
        """

        # Debugging
        error_handle = debug.ErrorOutput()
        deb = debug.ExecutionTiming()
        # Create loop for camera frames
        deb.check()

        with variables.lock:
            # Refresh frame
            self.camera.get_frame()

        # Get filtered image for processing
        _, filtered_image_gray = (
            get_filtered_image(self.camera.frame, variables.lower_range,
                               variables.upper_range))

        # Detect circles in filtered image but use try except to prevent
        # program from crashing when circles are not found
        while not variables.exit_gen:
            deb.check()

            with variables.lock:
                # Refresh frame
                self.camera.get_frame()

            # Get filtered image for processing
            _, filtered_image_gray = (
                get_filtered_image(self.camera.frame, variables.lower_range,
                                   variables.upper_range))

            # Detect circles in filtered image but use try except to prevent
            # program from crashing when circles are not found
            try:
                circles = cv2.HoughCircles(
                    filtered_image_gray, cv2.HOUGH_GRADIENT, 1, 50,
                    param1=variables.circle_detect_param,
                    param2=variables.circle_detect_param2,
                    minRadius=0, maxRadius=0)
                # Draw circles for visual representation of detection
                circles = np.uint16(np.around(circles))
                num_circles = draw_circles(
                    self.camera.frame, circles, self.camera.width,
                    self.camera.height)
                # If object detected send message to robot control
                if num_circles == 1:
                    with variables.lock:
                        if (variables.thread_motion_num == -1 and
                                variables.automatic_control):
                            variables.thread_motion_num = 2
                            variables.exit_gen = 1
            except Exception as e:
                error_handle.error_output(e)

            # Show full image with detected circles and filter
            cv2.imshow("Full image", self.camera.frame)

            k = cv2.waitKey(5) & 0xFF
            # End if user presses any key.
            # 255 is the default value for windows. -1 is the default on the
            # raspberry pi.
            if k == ord("s"):
                cv2.imwrite("full_image.jpg", self.camera.frame)
            if k != 255 and k != -1:
                break
            with variables.lock:
                if variables.exit_detect:
                    break
        k = cv2.waitKey(5) & 0xFF
        cv2.destroyAllWindows()
        # Return 0 to report success
        return 0

    # Create function to calibrate filter
    def calibrate_filter(self):
        """ Process:
        - Get previously stored variables from file.
        - Create track bars that are used to adjust the various filter
          parameters.
        - Continuously capture frames from the camera
        - Filter frame for selective color
        - Detect circles in filtered image.
        - Draw detected circles

        :return:

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
        cv2.createTrackbar("Lower top", filter_bars, variables.lower_limit2,
                           360,
                           lower_change2)
        cv2.createTrackbar("lower hue", filter_bars,
                           variables.lower_limit_hue,
                           360, lower_change3)
        cv2.createTrackbar("upper bottom", filter_bars, variables.upper_limit,
                           360, upper_change)
        cv2.createTrackbar("upper top", filter_bars, variables.upper_limit2,
                           360,
                           upper_change2)
        cv2.createTrackbar("upper hue", filter_bars,
                           variables.upper_limit_hue,
                           360, upper_change3)
        cv2.createTrackbar("circle param", circle_bars,
                           variables.circle_detect_param, 500,
                           circle_detect_change)
        cv2.createTrackbar("circle param 2", circle_bars,
                           variables.circle_detect_param2,
                           500, circle_detect_change2)

        # Debugging
        error_handle = debug.ErrorOutput()
        deb = debug.ExecutionTiming()
        # Create loop for camera frames
        while not variables.exit_gen:
            deb.check()

            # Create arrays for filter parameters
            variables.lower_range = np.array([variables.lower_limit_hue,
                                              variables.lower_limit,
                                              variables.lower_limit2])
            variables.upper_range = np.array([variables.upper_limit_hue,
                                              variables.upper_limit,
                                              variables.upper_limit2])
            with variables.lock:
                # Refresh frame
                self.camera.get_frame()
            # Get filtered image for processing
            filtered_image, filtered_image_gray = (
                get_filtered_image(self.camera.frame, variables.lower_range,
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
                draw_circles(self.camera.frame, circles, self.camera.width,
                             self.camera.height)
            except Exception as e:
                error_handle.error_output(e)

            # Show full image with detected circles and show filtered image
            cv2.imshow("Full image", self.camera.frame)
            cv2.imshow("filter", filtered_image)

            # Check to see if user is done adjusting filter.
            # End if user is done.
            k = cv2.waitKey(5) & 0xFF
            # Check to see if user does not want to save changes
            if k == ord("x"):
                print("not saving")
                break
            # Check to see if user wants to save a picture of full or full and
            # the filter
            elif k == ord("1"):
                cv2.imwrite("Full image.jpg", self.camera.frame)
                file_save()
                break
            elif k == ord("2"):
                cv2.imwrite("Full image.jpg", self.camera.frame)
                cv2.imwrite("filter.jpg", filtered_image)
                file_save()
                break
            # End if user presses any other key. 255 is the default value for
            # windows. -1 is the default on the raspberry pi
            elif k != 255 and k != -1:
                file_save()
                break
            with variables.lock:
                if variables.exit_calibrate:
                    break
        cv2.destroyAllWindows()


# Create function to draw circles
def draw_circles(image, circles, width, height, max_circles=60, buffer=5):
    """:param image:  opencv compatible array (current frame)
    :param circles: output from cv2.HoughCircles
    :param width: width of image
    :param height: height of image
    :param max_circles: limit the number of detected circles for testing
    :param buffer: used to increase the size of the box around the circle.

    :return: number of circles detected or -1 for error

    process: draw all the circles detected using cv2.HoughCircles and a
    box around all the circles.
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
        if debug.debug_circles:
            if (time.time() - variables.last_output_c
                    > variables.output_frequency):
                print("error too many circles  ", num_circles)
                variables.last_output_c = time.time()
        # Return error code
        return -1


# Create function to filter image. Then return the filtered image
def get_filtered_image(image, lower_range, upper_range):
    """:param image: camera frame
    :param lower_range: lower hsv range (array of 3 numbers)
    :param upper_range: upper hsv range (array of 3 numbers)

    :return: colored filtered image and gray filtered image.

    Process: take image and remove all colors out side of color range to
    create a mask. This mask is then used to create a filtered image.
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



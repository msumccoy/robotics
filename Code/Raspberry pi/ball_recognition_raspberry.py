""" Kuwin Wyke
Midwestern State University
Start: 10 October 2019
End: work in progress

This program detects a ball by using a filter that looks only for the color
of the ball. There is a function to manually calibrate the filter. Once only
the color of the ball is detected as input, the program looks for a circle
using a built ini OpenCV function. There is also a function to draw the
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
import platform

# Check if running on rasp pi to import pi cam modules
if platform.system() != "Windows":
    from picamera.array import PiRGBArray
    from picamera import PiCamera


# Create class to handle camera object
class Camera:
    """ This class is used to create a camera object. With this class
    both windows and raspberry pi will be able to use the same object because
    this class will handle the differences between the two operating systems.

    Additionally it will reduce code when implementing camera operations in
    different functions.
    """

    # Set a default height and width (if the dimensions are off the programing
    # language will correct it automatically I think.
    set_width = 320
    set_height = 240

    # Initialize the class. No variables are required because the only
    # condition is the operating system.
    def __init__(self):
        # Check if the operating system is linux, (raspberry pi will return
        # ("Linux"). The raspberry pi uses a pi cam and therefore needs
        # the pi cam implementation of the camera.
        if platform.system() == "Linux":
            # print("starting camera") #for debugging#########################
            self.cam = PiCamera()
            self.cam.resolution = (self.set_width, self.set_height)
            self.raw_capture = PiRGBArray(self.cam)
        else:
            # print("starting camera") #for debugging#########################
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, self.set_width)
            self.cap.set(4, self.set_height)
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
    commands to send to the robot."""
    # Variable to count how many times action is executed
    action_count = 0
    # Variable to set delay between executions of action (seconds)
    action_delay = 5
    # Variable to check the time action was executed last (time.time())
    action_last_execution = 0

    def action(self):
        """ This function is just to prove that action can be taken. Once
        the code is complete an actual action will be created.
        """
        delay = time.time() - self.action_last_execution
        # Ensure enough time has elapsed since last execution call to prevent
        # excesive calls to the same action.
        if delay > self.action_delay:
            self.action_count += 1
            self.action_last_execution = time.time()
            print("Action was called: ", self.action_count)


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
            if top_left_x < 0: top_left_x = 1
            if top_left_x > width: top_left_x = 1
            if top_left_y > height: top_left_y = 1
            if top_left_y < 0: top_left_y = 1
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

    # Set path to variables file
    variables_file = "filter_variables/filter_variables.txt"
    variables = open(variables_file, "r")
    lower_limit = int(variables.readline())
    lower_limit2 = int(variables.readline())
    lower_limit_hue = int(variables.readline())
    upper_limit = int(variables.readline())
    upper_limit2 = int(variables.readline())
    upper_limit_hue = int(variables.readline())
    circle_detect_param = int(variables.readline())
    circle_detect_param2 = int(variables.readline())
    variables.close()

    # Create function to save adjusted parameters
    def file_save():
        print("saving")
        string = str(lower_limit) + '\n'
        string += str(lower_limit2) + '\n'
        string += str(lower_limit_hue) + '\n'
        string += str(upper_limit) + '\n'
        string += str(upper_limit2) + '\n'
        string += str(upper_limit_hue) + '\n'
        string += str(circle_detect_param) + '\n'
        string += str(circle_detect_param2)
        variables = open(variables_file, "w")
        variables.write(string)
        variables.close()

    # Create functions to change parameters of hsv filter
    def lower_change(pos):
        nonlocal lower_limit
        lower_limit = pos

    def lower_change2(pos):
        nonlocal lower_limit2
        lower_limit2 = pos

    def lower_change3(pos):
        nonlocal lower_limit_hue
        lower_limit_hue = pos

    def upper_change(pos):
        nonlocal upper_limit
        upper_limit = pos

    def upper_change2(pos):
        nonlocal upper_limit2
        upper_limit2 = pos

    def upper_change3(pos):
        nonlocal upper_limit_hue
        upper_limit_hue = pos

    # Create functions to change circle detection parameters
    def circle_detect_change(pos):
        nonlocal circle_detect_param
        circle_detect_param = pos

    def circle_detect_change2(pos):
        nonlocal circle_detect_param2
        circle_detect_param2 = pos

    # Create variable for track bar names to make it easy to change
    filter_bars = "filter_bars"
    # Create second windows name to accommodate all bars
    circle_bars = "circle_bars"
    # Create named window to put track bars
    cv2.namedWindow(filter_bars)
    cv2.namedWindow(circle_bars)

    # Create Track bars to adjust filter and circle detection parameters
    cv2.createTrackbar("Lower bottom", filter_bars, lower_limit, 360,
                       lower_change)
    cv2.createTrackbar("Lower top", filter_bars, lower_limit2, 360,
                       lower_change2)
    cv2.createTrackbar("lower hue", filter_bars, lower_limit_hue, 360,
                       lower_change3)
    cv2.createTrackbar("upper bottom", filter_bars, upper_limit, 360,
                       upper_change)
    cv2.createTrackbar("upper top", filter_bars, upper_limit2, 360,
                       upper_change2)
    cv2.createTrackbar("upper hue", filter_bars, upper_limit_hue, 360,
                       upper_change3)
    cv2.createTrackbar("circle param", circle_bars, circle_detect_param, 500,
                       circle_detect_change)
    cv2.createTrackbar("circle param 2", circle_bars, circle_detect_param2,
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
        lower_range = np.array([lower_limit_hue, lower_limit, lower_limit2])
        upper_range = np.array([upper_limit_hue, upper_limit, upper_limit2])

        # Refresh frame
        camera.get_frame()
        # Get filtered image for processing
        filtered_image, filtered_image_gray = get_filtered_image(camera.frame,
                                                                 lower_range,
                                                                 upper_range)

        # Detect circles in filtered image but use try except to prevent
        # program from crashing when circles are not found
        try:
            circles = cv2.HoughCircles(filtered_image_gray,
                                       cv2.HOUGH_GRADIENT,
                                       1, 50, param1=circle_detect_param,
                                       param2=circle_detect_param2,
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


def main():
    """ input: none
    Process: Get filter variables from file. Get frames from camera
    continuously. Detect circles in each frame and draw circles along with
    bounding boxes. output image continuously
    output: none

    This function is incomplete at the moment.
    """

    # Set path to variables file
    variables_file = "filter_variables/filter_variables.txt"
    variables = open(variables_file, "r")
    lower_limit = int(variables.readline())
    lower_limit2 = int(variables.readline())
    lower_limit_hue = int(variables.readline())
    upper_limit = int(variables.readline())
    upper_limit2 = int(variables.readline())
    upper_limit_hue = int(variables.readline())
    circle_detect_param = int(variables.readline())
    circle_detect_param2 = int(variables.readline())
    variables.close()

    # Create robot object to initiate connection with the robot
    robot = Robot()
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

        # Create arrays for filter parameters
        lower_range = np.array([lower_limit_hue, lower_limit, lower_limit2])
        upper_range = np.array([upper_limit_hue, upper_limit, upper_limit2])
        # Refresh frame
        camera.get_frame()

        # Get filtered image for processing
        _, filtered_image_gray = get_filtered_image(camera.frame, lower_range,
                                                    upper_range)

        # Detect circles in filtered image but use try except to prevent
        # program from crashing when circles are not found
        try:
            circles = cv2.HoughCircles(filtered_image_gray,
                                       cv2.HOUGH_GRADIENT,
                                       1, 50, param1=circle_detect_param,
                                       param2=circle_detect_param2,
                                       minRadius=0, maxRadius=0)
            # Draw circles for visual representation of detection
            circles = np.uint16(np.around(circles))
            num_circles = draw_circles(camera.frame, circles, camera.width,
                                       camera.height)
            if num_circles == 1:
                robot.action()
        except Exception as e:
            # print(e) # for debugging #######################################
            pass

        # Show full image with detected circles and filter
        cv2.imshow("Full image", camera.frame)

        k = cv2.waitKey(5) & 0xFF
        # End if user presses any key. 255 is the default value for windows.
        # -1 is the default on the raspberry pi
        if k != 255 and k != -1:
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

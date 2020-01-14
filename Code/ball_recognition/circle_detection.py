""" Kuwin Wyke
Midwestern State University
Start: 6 November 2019
End: work in progress

This module is designed to be used in the ball recognition program in the
folder named "ball_recognition_v1". It contains functions that are to be used
by the "main.py" file to detect circles using a color filter. Additionally
it has a function to calibrate the filter
"""

import cv2
import numpy as np
import time

# Project specific modules
from camera import Camera
from constants import DICTS
from debug import Debug, ExecutionTiming, ErrorOutput
from motion_logic import MotionLogic
from robot_control import Robot
from variables import ExitControl, FilterVariables, RobotCom


class ObjectDetector:

    # Create circle detection code
    @staticmethod
    def object_detection(robot_type):
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
        robot = Robot.get_inst(robot_type)

        # Create camera object
        camera = Camera.get_inst()
        frame = camera.get_frame()
        height, width, channel = frame.shape

        filter_vars = FilterVariables.get_inst()

        # Debugging
        error_handle = ErrorOutput()
        deb = ExecutionTiming()

        # Create loop for camera frames
        while not ExitControl.gen and not ExitControl.detection:
            deb.check()
            frame = camera.get_frame()

            # Get filtered image for processing
            _, filtered_image_gray = (
                get_filtered_image(frame, filter_vars.lower_range,
                                   filter_vars.upper_range))

            # Detect circles in filtered image but use try except to prevent
            # program from crashing when circles are not found
            try:
                circles = cv2.HoughCircles(
                    filtered_image_gray, cv2.HOUGH_GRADIENT, 1, 50,
                    param1=filter_vars.circle_detect_param,
                    param2=filter_vars.circle_detect_param2,
                    minRadius=0, maxRadius=0)
                # Draw circles for visual representation of detection
                circles = np.uint16(np.around(circles))
                num_circles = draw_circles(frame, circles, width, height)
                # If object detected send message to robot control
                if num_circles == 1:
                    if RobotCom.automatic_control:
                        robot.play_rcb4_motion(
                            DICTS.HUMANOID_FULL[
                                MotionLogic.create_motion_num()
                            ]
                        )
            except Exception as e:
                error_handle.error_output(e)

            # Show full image with detected circles and filter
            cv2.imshow("Full image", frame)

            k = cv2.waitKey(5) & 0xFF
            # End if user presses any key.
            # 255 is the default value for windows. -1 is the default on the
            # raspberry pi.
            if k == ord("s"):
                cv2.imwrite("full_image.jpg", frame)
            if k != 255 and k != -1:
                ExitControl.detection = 1
        cv2.destroyAllWindows()
        # Return 0 to report success
        return 0

    # Create function to calibrate filter
    @staticmethod
    def calibrate_filter():
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
        # Debugging
        error_handle = ErrorOutput()
        deb = ExecutionTiming()

        filter_vars = FilterVariables.get_inst()
        camera = Camera.get_inst()
        frame = camera.get_frame()
        height, width, channel = frame.shape

        # Create variable for track bar names to make it easy to change
        filter_bars = "filter_bars"
        # Create second windows name to accommodate all bars
        circle_bars = "circle_bars"
        # Create named window to put track bars
        cv2.namedWindow(filter_bars)
        cv2.namedWindow(circle_bars)

        # Create Track bars to adjust filter and circle detection parameters
        cv2.createTrackbar("Lower bottom", filter_bars,
                           filter_vars.lower_limit, 360,
                           filter_vars.update_lower_limit)
        cv2.createTrackbar("Lower top", filter_bars,
                           filter_vars.lower_limit2, 360,
                           filter_vars.update_lower_limit2)
        cv2.createTrackbar("lower hue", filter_bars,
                           filter_vars.lower_limit_hue, 360,
                           filter_vars.update_lower_limit_hue)
        cv2.createTrackbar("upper bottom", filter_bars,
                           filter_vars.upper_limit, 360,
                           filter_vars.update_upper_limit)
        cv2.createTrackbar("upper top", filter_bars,
                           filter_vars.upper_limit2, 360,
                           filter_vars.update_upper_limit2)
        cv2.createTrackbar("upper hue", filter_bars,
                           filter_vars.upper_limit_hue, 360,
                           filter_vars.update_upper_limit_hue)
        cv2.createTrackbar("circle param", circle_bars,
                           filter_vars.circle_detect_param, 500,
                           filter_vars.update_circle_detect_param)
        cv2.createTrackbar("circle param 2", circle_bars,
                           filter_vars.circle_detect_param2, 500,
                           filter_vars.update_circle_detect_param2)

        # Create loop for camera frames
        while not ExitControl.gen and not ExitControl.calibrate:
            deb.check()

            # Get filtered image for processing
            filter_vars.update_ranges()
            filtered_image, filtered_image_gray = (get_filtered_image(
                    frame, filter_vars.lower_range, filter_vars.upper_range))

            # Detect circles in filtered image but use try except to prevent
            # program from crashing when circles are not found
            try:
                circles = cv2.HoughCircles(
                    filtered_image_gray, cv2.HOUGH_GRADIENT, 1, 50,
                    param1=filter_vars.circle_detect_param,
                    param2=filter_vars.circle_detect_param2,
                    minRadius=0, maxRadius=0)
                # Draw circles for visual representation of detection
                circles = np.uint16(np.around(circles))
                draw_circles(frame, circles, width, height)
            except Exception as e:
                error_handle.error_output(e)

            # Show full image with detected circles and show filtered image
            cv2.imshow("Full image", frame)
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
                cv2.imwrite("Full image.jpg", frame)
                filter_vars.file_save()
                break
            elif k == ord("2"):
                cv2.imwrite("Full image.jpg", frame)
                cv2.imwrite("filter.jpg", filtered_image)
                filter_vars.file_save()
                break
            # End if user presses any other key. 255 is the default value for
            # windows. -1 is the default on the raspberry pi
            elif k != 255 and k != -1:
                filter_vars.file_save()
                break

            frame = camera.get_frame()
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
    for _ in circles[0, :]:
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
        """need to re-implement debugging"""
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

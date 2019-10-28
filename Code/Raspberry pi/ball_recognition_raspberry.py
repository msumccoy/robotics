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

Programed on windows and tested on windows and raspberry pi.
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

def draw_circles(image, circles, width, height, max_circles=60, buffer=5):
    """ This function is used to draw a circle and or box around a circle.
    This function is to be used after the opencv function HoughCircles().

    width and height are the width and height of the image.
    buffer is used to make the box a little larger than the circle
    """
    # Count the number of circles to prevent the system from getting
    # bogged down trying to draw too many circles
    count = 0
    for i in circles[0, :]:
        count += 1
    if count <= max_circles:
        for i in circles[0, :]:
            # Get cordinated for top and bottom of the box
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
    else:
        print("error too many circles  ", count)

# Create function to calibrate filter
def calibrate_filter(calibrate = True):
    """ This module is used to fine tune the variables for filtering out
    the color of the ball and ball detection parameters.
    """
    variables = open("filter_variables.txt", "r")
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
        string = str(lower_limit) + '\n'
        string += str(lower_limit2) + '\n'
        string += str(lower_limit_hue) + '\n'
        string += str(upper_limit) + '\n'
        string += str(upper_limit2) + '\n'
        string += str(upper_limit_hue) + '\n'
        string += str(circle_detect_param) + '\n'
        string += str(circle_detect_param2)
        variables = open("filter_variables.txt", "w")
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

    # Check platform to determine how to start camera
    if platform.system() != "Windows":
        print("starting camera")
        camera = PiCamera()
        camera.resolution = (320, 240)
        raw_capture = PiRGBArray(camera)
    else:
        cap = cv2.VideoCapture(0)
        cap.set(3, 320)
        cap.set(4, 240)
    # Loop for each frame for video
    time1 = time.time()
    cycles = 0
    # Create infinite loop for camera frames
    while 1:
        # Calculate average frame processing time
        cycles += 1
        total_time = time.time() - time1
        average = total_time / cycles
        print("Total = ", total_time)
        print("Average = ", average)

        # Create arrays for filter parameters
        lower_range = np.array([lower_limit_hue, lower_limit, lower_limit2])
        upper_range = np.array([upper_limit_hue, upper_limit, upper_limit2])

        # Determine platform for camera specific methods to be used
        if platform.system() != "Windows":
            camera.capture(raw_capture, "bgr", True)
            frame = raw_capture.array
            raw_capture.truncate(0)
        else:
            _, frame = cap.read()

        height, width, channels = frame.shape

        # Create filter
        # Get hsv color scheme
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Threshold the hsv color scheme to get only desired colors
        mask = cv2.inRange(hsv, lower_range, upper_range)

        # Use bitwise and to find only regions of the original picture that
        # match the color you are looking for
        filtered_image = cv2.bitwise_and(frame, frame, mask=mask)

        # Conver filtered image to gray scale. Image cannot be converted to
        # gray scale immediately. Convert anything but hsv to BRG first.
        filtered_image = cv2.medianBlur(filtered_image, 3)
        filtered_image_gray = cv2.cvtColor(filtered_image, cv2.COLOR_HLS2BGR)
        filtered_image_gray = cv2.cvtColor(filtered_image_gray,
                                           cv2.COLOR_BGR2GRAY)

        # Detect circles in filtered image but use try except to prevent
        # program from crashing when circles are not found
        try:
            circles = cv2.HoughCircles(filtered_image_gray, cv2.HOUGH_GRADIENT,
                                       1, 50, param1=circle_detect_param,
                                       param2=circle_detect_param2,
                                       minRadius=0, maxRadius=0)
            # Draw circles for visual representation of detection
            circles = np.uint16(np.around(circles))
            draw_circles(frame, circles, width, height)
        except Exception as e:
            print(e)

        # Show full image with detected circles and filter
        cv2.imshow("Full image", frame)
        # Only show filter window if calibration set to yes
        if calibrate:
            cv2.imshow("filter", filtered_image)

        # Check to see if user is done adjusting filter. End if user is done.
        k = cv2.waitKey(5) & 0xFF
        # Check to see if user does not want to save changes
        if k == ord("x"):
            break
        # Check to see if user wants to save a picture of full or full and
        # the filter
        elif k == ord("1"):
            cv2.imwrite("Full image.jpg", frame)
            file_save()
            break
        elif k == ord("2"):
            cv2.imwrite("Full image.jpg", frame)
            cv2.imwrite("filter.jpg", filtered_image)
            file_save()
            break
        # End if user presses any other key. 255 is the default value
        elif k != 255 and k != -1:
            file_save()
            break

    # Close camera connection and all openCV windows
    if platform.system() != "Windows":
        camera.close()
    else:
        cap.release()
    cv2.destroyAllWindows()

def track_ball():
    """ This function will be to track the ball
    incomplete.....
    """
    calibrate_filter(False)

def test():
    # function to be discarded
    cap = cv2.VideoCapture(0)
    _, frame = cap.read()
    cap.release()
    cv2.imshow("Frame_original", frame)



    cv2.waitKey(0)
    cv2.destroyAllWindows()

def test2():
    # function to be discarded
    start = time.time()
    import cv2 as cv
    print(time.time()-start)# to delete ######################################################
    # Set up training data
    labels = np.array([1, -1, -1, 1])
    trainingData = np.matrix([[501, 10], [255, 10], [501, 255], [10, 501]],
                             dtype=np.float32)
    print(time.time()-start)# to delete #######################################################
    # Train the SVM
    svm = cv.ml.SVM_create()
    svm.setType(cv.ml.SVM_C_SVC)
    svm.setKernel(cv.ml.SVM_LINEAR)
    svm.setTermCriteria((cv.TERM_CRITERIA_MAX_ITER, 100, 1e-6))
    svm.train(trainingData, cv.ml.ROW_SAMPLE, labels)
    # Data for visual representation
    width = 512
    height = 512
    image = np.zeros((height, width, 3), dtype=np.uint8)
    # Show the decision regions given by the SVM
    green = (0, 255, 0)
    blue = (255, 0, 0)
    print(time.time()-start)# to delete############################################################
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            sampleMat = np.matrix([[j, i]], dtype=np.float32)
            response = svm.predict(sampleMat)[1]
            if response == 1:
                image[i, j] = green
            elif response == -1:
                image[i, j] = blue
    # Show the training data
    print(
        time.time() - start)  # to delete######################################################
    thickness = -1
    cv.circle(image, (501, 10), 5, (0, 0, 0), thickness)
    cv.circle(image, (255, 10), 5, (255, 255, 255), thickness)
    cv.circle(image, (501, 255), 5, (255, 255, 255), thickness)
    cv.circle(image, (10, 501), 5, (255, 255, 255), thickness)
    # Show support vectors
    thickness = 2
    sv = svm.getUncompressedSupportVectors()
    print(time.time()-start)#######################################################
    for i in range(sv.shape[0]):
        cv.circle(image, (sv[i, 0], sv[i, 1]), 6, (128, 128, 128), thickness)
    cv.imwrite('result.png', image)  # save the image
    cv.imshow('SVM Simple Example', image)  # show it to the user
    cv.waitKey()
    cv.destroyAllWindows()
    end = time.time() - start#####################################################
    print(end)#####################################################################

def raspi_test():
    """ This function is only to test some functionality on the raspberry pi
    only (not for windows)
    """
    camera = PiCamera()
    camera.resolution = (320, 240)
    raw_capture = PiRGBArray(camera)
    start = time.time()
    count = 0
    while 1:
        count += 1
        average = (time.time() - start) / count
        camera.capture(raw_capture, "bgr", True)
        frame = raw_capture.array
        raw_capture.truncate(0)
        cv2.imshow("p", frame)
        k = cv2.waitKey(5) & 0xFF
        if k != 255 and k != -1:
            break
        print(count)
        print(average)
    cv2.destroyAllWindows()
    camera.close()

def main():
    calibrate_filter()

if __name__ == "__main__":
    main()
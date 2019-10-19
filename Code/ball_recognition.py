""" Kuwin Wyke
Midwestern State University
Start: 10 October 2019
End: work in progress

This program detects a ball by using a filter that looks only for the color
of the ball. There is a function to manually calibrate the filter. Once only
the color of the ball is detected as input, the program looks for a circle
using a built ini OpenCV function.

Programed and tested on windows.
"""

import cv2
import numpy as np

# Create function to calibrate filter
def calibrate_filter():
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
    # Set maximum number of circles
    max_circles = 60
    # Set buffer to increase size of the box around each circle
    buffer = 5

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

    # Create variable for track bar names to make it easy to change
    filter_bars = "filter_bars"
    # Create second windows name to accomodate all bars
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

    # Start camera before loop to ensure it is working
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    # Loop for each frame for video
    while ret:
        # Create arrays for filter parameters
        lower_range = np.array([lower_limit_hue, lower_limit, lower_limit2])
        upper_range = np.array([upper_limit_hue, upper_limit, upper_limit2])

        ret, frame = cap.read()

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
        filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_HLS2BGR)
        filtered_image = cv2.medianBlur(filtered_image, 3)
        filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2GRAY)

        # Detect circles in filtered image but use try except to prevent
        # program from crashing when circles are not found
        try:
            circles = cv2.HoughCircles(filtered_image, cv2.HOUGH_GRADIENT,
                                       1, 50, param1=circle_detect_param,
                                       param2=circle_detect_param2,
                                       minRadius=0, maxRadius=0)

            # Draw circles for visual representation of detection
            circles = np.uint16(np.around(circles))
            # Count the number of circles to prevent the system from getting
            # bogged down trying to draw too many circles
            count = 0
            for i in circles[0, :]:
                count += 1
            if count <= max_circles:
                for i in circles[0, :]:
                    # draw black box
                    top_left_x = i[0] - i[2] +- buffer
                    top_left_y = i[1] - i[2] - buffer
                    bottom_right_x = i[0] + i[2] + buffer
                    bottom_right_y = i[1] + i[2] + buffer
                    cv2.rectangle(frame,(top_left_x, top_left_y),
                                  (bottom_right_x, bottom_right_y),
                                  (0, 0, 0), 0)
                    # draw the outer circle
                    cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
                    # draw the center of the circle
                    cv2.circle(frame, (i[0], i[1]), 2, (0, 0, 255), 3)
            else:
                print("error too many circles")
        except Exception as e:
            print(e)

        # Show full image with detected circles and filter
        cv2.imshow("Full image", frame)
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
        elif k != 255:
            file_save()
            break

    # Close camera connection and all openCV windows
    cap.release()
    cv2.destroyAllWindows()

def main():
    calibrate_filter()

if __name__ == "__main__":
    main()
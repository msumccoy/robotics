"""
Kuwin Wyke
Midwestern State University

This program is designed to measure the different speeds of detection
algorithms. The detection algorithms this program will be measuring are
haar detection and tensorflow inference graphs.

This program is designed to utilize a dual lens camera that outputs two images
in a side by side array
"""
import cv2
import logging
import os
import time
import numpy as np

from camera_control import CameraControl
from config import Conf, Log, Display, Templates
from haar_detection import haar_detection


def main():
    # Ensure logging folder exist to avoid potential errors
    if not os.path.exists(Log.ROOT):
        os.mkdir(Log.ROOT)

    # Set up loggers
    last_log = 0
    main_logger = logging.getLogger(Log.MAIN_NAME)
    haar_logger = logging.getLogger(Log.HAAR_NAME)
    tf_logger = logging.getLogger(Log.TF_NAME)

    main_logger.setLevel(Log.BASE_LEVEL)
    haar_logger.setLevel(Log.BASE_LEVEL)
    tf_logger.setLevel(Log.BASE_LEVEL)

    main_file_handler = logging.FileHandler(Log.MAIN)
    haar_file_handler = logging.FileHandler(Log.HAAR)
    tf_file_handler = logging.FileHandler(Log.TF)

    formatter = logging.Formatter(Log.FORMAT)
    main_file_handler.setFormatter(formatter)
    haar_file_handler.setFormatter(formatter)
    tf_file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    main_logger.addHandler(main_file_handler)
    main_logger.addHandler(stream_handler)
    haar_logger.addHandler(haar_file_handler)
    haar_logger.addHandler(stream_handler)
    tf_logger.addHandler(tf_file_handler)
    tf_logger.addHandler(stream_handler)

    # Instantiate camera
    cam = CameraControl.get_inst()

    # Start timers
    start = time.time()
    time1 = time.time()
    # Set exit flag
    not_exit = True
    while not_exit:
        loop_time = time.time() - time1
        time1 = time.time()

        # Refresh frame of camera
        cam.refresh_frame()

        ######################################################################
        # Haar Detection #####################################################
        ######################################################################
        # Detect balls in left image, time the detection, draw bounding boxes
        # around the detected balls
        haar_l_detect_time, haar_l_points = haar_detection(cam.haar_left)
        haar_l_num_balls = len(haar_l_points)

        # Detect balls in right image, time the detection, draw bounding boxes
        # around the detected balls
        haar_r_detect_time, haar_r_points = haar_detection(cam.haar_right)
        haar_r_num_balls = len(haar_r_points)

        if haar_l_num_balls == haar_r_num_balls:
            haar_num_balls = haar_l_num_balls
        else:
            haar_num_balls = "Not Equal"

        ######################################################################
        # TensorFlow Detection ###############################################
        ######################################################################
        # Detect balls in left image, time the detection, draw bounding boxes
        # around the detected balls
        tf_l_detect_time, tf_l_points = 0, ((0, 0),)
        tf_l_num_balls = len(tf_l_points)

        # Detect balls in right image, time the detection, draw bounding boxes
        # around the detected balls
        tf_r_detect_time, tf_r_points = 0, ((0, 0),)
        tf_r_num_balls = len(tf_r_points)

        if tf_l_num_balls == tf_r_num_balls:
            tf_num_balls = tf_l_num_balls
        else:
            tf_num_balls = "Not Equal"

        ######################################################################
        # Comparision and metric calculations ################################
        ######################################################################
        # Find which detection was faster
        haar_detect_time = haar_l_detect_time + haar_r_detect_time
        tf_detect_time = tf_l_detect_time + tf_r_detect_time
        if haar_detect_time < tf_detect_time:
            fastest_detector = "Haar Cascade detection"
        else:
            fastest_detector = "TensorFlow Inference graph"

        # Check if same number of balls were detected
        if tf_num_balls == haar_num_balls:
            num_balls = tf_num_balls
        else:
            num_balls = "Detection not similar"

        ######################################################################
        # Set up haar dipslay area ###########################################
        ######################################################################
        # Create display areas
        haar_display_area = np.zeros_like(
            cam.haar_frame
        )[0:Display.MAX_DISP_AREA_H]
        tf_display_area = haar_display_area.copy()

        # Round time figures to 2 decimal places
        from_start_time = f"{time.time() - start:.2f}"
        loop_time = f"{loop_time:.2f}"
        haar_l_detect_time = f"{haar_l_detect_time:.2f}"
        haar_r_detect_time = f"{haar_r_detect_time:.2f}"
        tf_l_detect_time = f"{tf_l_detect_time:.2f}"
        tf_r_detect_time = f"{tf_r_detect_time:.2f}"

        # Add total time and total number of items detected
        cv2.putText(
            img=haar_display_area,
            text=Templates.TOT_TIME.substitute(
                time=loop_time
            ),
            org=(Display.TEXT_START_X, Display.TEXT_START_Y),
            fontFace=Display.FONT,
            fontScale=Display.SCALE,
            color=Display.COLOR1
        )
        cv2.putText(
            img=haar_display_area,
            text=Templates.TOT_BALLS_DETECTED.substitute(
                num_balls=haar_num_balls
            ),
            org=(cam.mid_point + Display.TEXT_START_X, Display.TEXT_START_Y),
            fontFace=Display.FONT,
            fontScale=Display.SCALE,
            color=Display.COLOR1
        )
        # Add time for left and right detection
        cv2.putText(
            img=haar_display_area,
            text=Templates.LEFT_TIME.substitute(
                time=haar_l_detect_time
            ),
            org=(Display.TEXT_START_X, Display.TEXT_START_Y * 2),
            fontFace=Display.FONT,
            fontScale=Display.SCALE,
            color=Display.COLOR1
        )
        cv2.putText(
            img=haar_display_area,
            text=Templates.RIGHT_TIME.substitute(
                time=haar_r_detect_time
            ),
            org=(
                cam.mid_point + Display.TEXT_START_X,
                Display.TEXT_START_Y * 2
            ),
            fontFace=Display.FONT,
            fontScale=Display.SCALE,
            color=Display.COLOR1
        )
        # Add number of items detected in left and right image
        cv2.putText(
            img=haar_display_area,
            text=Templates.LEFT_BALLS_DETECTED.substitute(
                num_balls=haar_l_num_balls
            ),
            org=(Display.TEXT_START_X, Display.TEXT_START_Y * 3),
            fontFace=Display.FONT,
            fontScale=Display.SCALE,
            color=Display.COLOR1
        )
        cv2.putText(
            img=haar_display_area,
            text=Templates.RIGHT_BALLS_DETECTED.substitute(
                num_balls=haar_r_num_balls
            ),
            org=(
                cam.mid_point + Display.TEXT_START_X,
                Display.TEXT_START_Y * 3
            ),
            fontFace=Display.FONT,
            fontScale=Display.SCALE,
            color=Display.COLOR1
        )
        cv2.putText(
            img=haar_display_area,
            text=Templates.TIME_FROM_START.substitute(
                time=from_start_time
            ),
            org=(Display.TEXT_START_X, Display.TEXT_START_Y * 4),
            fontFace=Display.FONT,
            fontScale=Display.SCALE,
            color=Display.COLOR1
        )

        ######################################################################
        # Set up tensorflow dipslay area #####################################
        ######################################################################
        # Add total time and total number of items detected
        cv2.putText(
            img=tf_display_area,
            text=Templates.TOT_TIME.substitute(
                time=loop_time
            ),
            org=(Display.TEXT_START_X, Display.TEXT_START_Y),
            fontFace=Display.FONT,
            fontScale=Display.SCALE,
            color=Display.COLOR1
        )
        cv2.putText(
            img=tf_display_area,
            text=Templates.TOT_BALLS_DETECTED.substitute(
                num_balls=tf_num_balls
            ),
            org=(cam.mid_point + Display.TEXT_START_X, Display.TEXT_START_Y),
            fontFace=Display.FONT,
            fontScale=Display.SCALE,
            color=Display.COLOR1
        )
        # Add time for left and right detection
        cv2.putText(
            img=tf_display_area,
            text=Templates.LEFT_TIME.substitute(
                time=tf_l_detect_time
            ),
            org=(Display.TEXT_START_X, Display.TEXT_START_Y * 2),
            fontFace=Display.FONT,
            fontScale=Display.SCALE,
            color=Display.COLOR1
        )
        cv2.putText(
            img=tf_display_area,
            text=Templates.RIGHT_TIME.substitute(
                time=tf_r_detect_time
            ),
            org=(
                cam.mid_point + Display.TEXT_START_X,
                Display.TEXT_START_Y * 2
            ),
            fontFace=Display.FONT,
            fontScale=Display.SCALE,
            color=Display.COLOR1
        )
        # Add number of items detected in left and right image
        cv2.putText(
            img=tf_display_area,
            text=Templates.LEFT_BALLS_DETECTED.substitute(
                num_balls=tf_l_num_balls
            ),
            org=(Display.TEXT_START_X, Display.TEXT_START_Y * 3),
            fontFace=Display.FONT,
            fontScale=Display.SCALE,
            color=Display.COLOR1
        )
        cv2.putText(
            img=tf_display_area,
            text=Templates.RIGHT_BALLS_DETECTED.substitute(
                num_balls=tf_r_num_balls
            ),
            org=(
                cam.mid_point + Display.TEXT_START_X,
                Display.TEXT_START_Y * 3
            ),
            fontFace=Display.FONT,
            fontScale=Display.SCALE,
            color=Display.COLOR1
        )
        cv2.putText(
            img=tf_display_area,
            text=Templates.TIME_FROM_START.substitute(
                time=from_start_time
            ),
            org=(Display.TEXT_START_X, Display.TEXT_START_Y * 4),
            fontFace=Display.FONT,
            fontScale=Display.SCALE,
            color=Display.COLOR1
        )

        #####################################################################
        # Show images #######################################################
        #####################################################################
        # Combine display areas with their respective images
        cam.haar_frame = np.concatenate(
            (cam.haar_frame,haar_display_area), axis=0
        )
        cam.tf_frame = np.concatenate(
            (cam.tf_frame, tf_display_area), axis=0
        )

        cv2.imshow(Display.WINDOW_HAAR, cam.haar_frame)
        cv2.imshow(Display.WINDOW_TF, cam.tf_frame)
        cam.record()

        ######################################################################
        # Logging ############################################################
        ######################################################################
        # Log the information
        main_logger.debug(
            Templates.TIME_TAKEN.substitute(
                time=from_start_time,
                tot=loop_time,
                haar_l=haar_l_detect_time,
                haar_r=haar_r_detect_time,
                tf_l=tf_l_detect_time,
                tf_r=tf_r_detect_time,
            )
        )
        main_logger.debug(
            Templates.FASTEST_DETECTION.substitute(
                fastest=fastest_detector
            )
        )
        main_logger.debug(
            Templates.BALLS_DETECTED.substitute(
                time=from_start_time,
                balls=num_balls,
                haar_balls=haar_num_balls,
                tf_balls=tf_num_balls
            )
        )

        haar_logger.debug(
            Templates.HAAR_TIME_TAKEN.substitute(
                time=from_start_time,
                haar_l=haar_l_detect_time,
                haar_r=haar_r_detect_time,
            )
        )
        haar_logger.debug(
            Templates.HAAR_BALLS_DETECTED.substitute(
                time=from_start_time,
                balls=num_balls,
                haar_balls=haar_num_balls,
            )
        )

        tf_logger.debug(
            Templates.TF_TIME_TAKEN.substitute(
                time=from_start_time,
                tf_l=tf_l_detect_time,
                tf_r=tf_r_detect_time,
            )
        )
        tf_logger.debug(
            Templates.TF_BALLS_DETECTED.substitute(
                time=from_start_time,
                balls=num_balls,
                tf_balls=tf_num_balls,
            )
        )

        if time.time() - last_log > Log.INTERVAL:
            last_log = time.time()
            main_logger.info(
                Templates.TIME_TAKEN.substitute(
                    time=from_start_time,
                    tot=loop_time,
                    haar_l=haar_l_detect_time,
                    haar_r=haar_r_detect_time,
                    tf_l=tf_l_detect_time,
                    tf_r=tf_r_detect_time,
                )
            )
            main_logger.info(
                Templates.FASTEST_DETECTION.substitute(
                    fastest=fastest_detector
                )
            )
            main_logger.info(
                Templates.BALLS_DETECTED.substitute(
                    time=from_start_time,
                    balls=num_balls,
                    haar_balls=haar_num_balls,
                    tf_balls=tf_num_balls
                )
            )

            haar_logger.info(
                Templates.HAAR_TIME_TAKEN.substitute(
                    time=from_start_time,
                    haar_l=haar_l_detect_time,
                    haar_r=haar_r_detect_time,
                )
            )
            haar_logger.info(
                Templates.HAAR_BALLS_DETECTED.substitute(
                    time=from_start_time,
                    balls=num_balls,
                    haar_balls=haar_num_balls,
                )
            )

            tf_logger.info(
                Templates.TF_TIME_TAKEN.substitute(
                    time=from_start_time,
                    tf_l=tf_l_detect_time,
                    tf_r=tf_r_detect_time,
                )
            )
            tf_logger.info(
                Templates.TF_BALLS_DETECTED.substitute(
                    time=from_start_time,
                    balls=num_balls,
                    tf_balls=tf_num_balls,
                )
            )

        k = cv2.waitKey(1)
        if k != -1 and k != 255:
            not_exit = False

    # Destroy all cv2 windows, release camera object,
    # release video object(conditional)
    cam.close()


# Only execute this code if it is calling it self
if __name__ == '__main__':
    main()

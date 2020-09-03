"""
Kuwin Wyke
Midwestern State University

This module is used to control all camera related operations within this
project
"""
import cv2

from config import Templates, Conditionals, Conf, Display


class CameraControl:
    """
    This class in the primary interface for all camera interactions

    This class will ave to be heavily modified when use of raspberry pi cam is
    implemented
    """
    _inst = None

    @staticmethod
    def get_inst():
        # Singleton
        if CameraControl._inst is None:
            CameraControl._inst = CameraControl()
        return CameraControl._inst

    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        _, self.tf_frame = self.cam.read()
        self.haar_frame = self.tf_frame.copy()
        self.haar_left = None
        self.tf_left =None
        self.haar_right = None
        self.tf_right = None
        self.mid_point = None
        if Conditionals.RECORD:
            height, width, _ = self.haar_frame.shape
            if height < Display.MAX_DISP_AREA_H:
                height *= 2
            else:
                height = Display.MAX_DISP_AREA_H
            self.haar_writer = cv2.VideoWriter(
                Conf.HAAR_VIDEO_FILE,
                cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                30,
                (width, height)
            )
            self.tf_writer = cv2.VideoWriter(
                Conf.TF_VIDEO_FILE,
                cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                30,
                (width, height)
            )

    def refresh_frame(self):
        """
        This method is used to get a new frame from the camera then create
        images for the left and right lens to draw boxes for tensorflow and
        haar cascades independently.
        """
        # Get new frame.
        _, self.tf_frame = self.cam.read()
        # Copy frame to allow drawing directly on left and right images
        self.haar_frame = self.tf_frame.copy()

        # Get Left and right images (left lens and right lens)
        height, width, _ = self.haar_frame.shape
        self.mid_point = int(width / 2)
        self.haar_left = self.haar_frame[0:height, 0:self.mid_point]
        self.tf_left = self.tf_frame[0:height, 0:self.mid_point]
        self.haar_right = self.haar_frame[0:height, self.mid_point:width]
        self.tf_right = self.tf_frame[0:height, self.mid_point:width]

    def record(self):
        if Conditionals.RECORD:
            self.haar_writer.write(self.haar_frame)
            self.tf_writer.write(self.tf_frame)

    def close(self):
        self.cam.release()

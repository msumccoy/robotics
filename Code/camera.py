"""
Kuwin Wyke
Midwestern State University
"""
import json
import logging
import time
import cv2

import log_set_up
from misc import get_int, get_float, get_specific_response, pretty_time
from config import Conf
from enums import RobotType, LensType, DistanceType
from variables import ExitControl


class Camera:
    _inst = {}
    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
    logger = logging.getLogger(Conf.LOG_CAM_NAME)

    @staticmethod
    def get_inst(
            cam_name, cam_num=0, lens_type=LensType.SINGLE, record=False
    ):
        if cam_name not in Camera._inst:
            Camera._inst[cam_name] = Camera(cam_num, lens_type, record)
        return Camera._inst[cam_name]

    def __init__(self, cam_num, lens_type, record):
        self.logger.debug(
            f"Cam started:\n"
            f"- cam_num: {cam_num}\n"
            f"- lens_type: {lens_type}\n"
            f"- record: {record}"
        )
        self.start = time.time()
        self.count = 0
        if lens_type != LensType.SINGLE and lens_type != LensType.DOUBLE:
            self.logger.exception(f"'{lens_type}' is not a valid lens type")
            self.main_logger.exception(
                f"Camera crashed -- '{lens_type}' is not a valid lens type"
            )
            raise ValueError(f"'{lens_type}' is not a valid lens type")
        self.cam = cv2.VideoCapture(cam_num)
        self.ret, self.frame = self.cam.read()
        self.lens_type = lens_type

        with open(Conf.CAM_SETTINGS_FILE) as file:
            self.settings = json.load(file)
        self.profile = Conf.CS_DEFAULT
        self.focal_len = None
        self.obj_width = None
        self.height, self.width, _ = self.frame.shape

        self.frame_left = None
        self.frame_right = None
        self.midpoint = None
        if lens_type == LensType.DOUBLE:
            self.get_dual_image()
            if self.height > self.width / 2:
                self.logger.warning(Conf.WARN_CAM_TYPE.substitute())

        self.record = record
        if record:
            self.logger.info("Recording active")
            width = self.width
            height = self.height
            self.video_writer = cv2.VideoWriter(
                Conf.CV_VIDEO_FILE,
                cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                10, (width, height)
            )

        self.objects = {}
        self.num_objects = 0
        self.num_left = 0
        self.num_right = 0
        self.detected_objects = None
        self.detected_left = None
        self.detected_right = None
        self.is_detected_equal = True
        self.is_detected = False
        track_bar = Conf.CV_WINDOW
        track_bar_scale = 4
        track_bar_neigh = 4
        if Conf.CS_DEFAULT in self.settings:
            if Conf.CS_FOCAL in self.settings[Conf.CS_DEFAULT]:
                track_bar_scale = (
                    (self.settings[self.profile][Conf.CS_SCALE] - 1.005) / 0.1
                )
                track_bar_scale = int(f"{track_bar_scale: .0f}")
            if Conf.CS_NEIGH in self.settings[Conf.CS_DEFAULT]:
                track_bar_neigh = self.settings[self.profile][Conf.CS_NEIGH]
        cv2.namedWindow(Conf.CV_WINDOW)
        cv2.namedWindow(track_bar)
        cv2.createTrackbar(
            "scale", track_bar, track_bar_scale, 89, self.set_scale
        )
        cv2.createTrackbar(
            "min Neigh", track_bar, track_bar_neigh, 50, self.set_neigh
        )
        if Conf.CS_DEFAULT not in self.settings:
            self.setup_profile(self.profile)
        self.update_instance_settings()
        self.logger.debug(
            f"Cam init ran in {pretty_time(self.start)}"
        )

    def start_recognition(self):
        self.logger.debug("start_recognition started")
        while self.settings[self.profile][Conf.CS_LENS_TYPE] != self.lens_type.value:
            self.logger.info(
                "Lens type of camera and settings profile do not match. "
                "Please fix"
            )
            self.calibrate()
        while not ExitControl.gen:
            self.ret, self.frame = self.cam.read()
            if self.lens_type == LensType.DOUBLE:
                self.get_dual_image()
            self.detect_object()
            cv2.imshow(Conf.CV_WINDOW, self.frame)
            if self.lens_type == LensType.DOUBLE:
                cv2.imshow(Conf.CV_WINDOW_LEFT, self.frame_left)
                cv2.imshow(Conf.CV_WINDOW_RIGHT, self.frame_right)
            if self.record:
                self.video_writer.write(self.frame)
            k = cv2.waitKey(50)
            if k == 27:
                ExitControl.gen = True

    def detect_object(self):
        if self.lens_type == LensType.SINGLE:
            gray_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            self.detected_objects = Conf.CV_DETECTOR.detectMultiScale(
                gray_frame,
                self.settings[self.profile][Conf.CS_SCALE],
                self.settings[self.profile][Conf.CS_NEIGH],
            )
            if self.detected_objects is not None:
                self.num_objects = len(self.detected_objects)
            else:
                self.num_objects = 0
        elif self.lens_type == LensType.DOUBLE:
            gray_left = cv2.cvtColor(self.frame_left, cv2.COLOR_BGR2GRAY)
            gray_right = cv2.cvtColor(self.frame_right, cv2.COLOR_BGR2GRAY)
            self.detected_left = Conf.CV_DETECTOR.detectMultiScale(
                gray_left,
                self.settings[self.profile][Conf.CS_SCALE],
                self.settings[self.profile][Conf.CS_NEIGH],
            )
            self.detected_right = Conf.CV_DETECTOR.detectMultiScale(
                gray_right,
                self.settings[self.profile][Conf.CS_SCALE],
                self.settings[self.profile][Conf.CS_NEIGH],
            )
            self.num_left = len(self.detected_left)
            self.num_right = len(self.detected_right)
            self.num_objects = self.num_left
            if self.num_left == self.num_right:
                self.is_detected_equal = True
            else:
                self.is_detected_equal = False
                if self.num_right > self.num_left:
                    self.num_objects = self.num_right

        ######################################################################
        # Draw bounding boxes and record distances ect.  #####################
        ######################################################################
        # Formula: F = (P x  D) / W
        # Transposed: D = (F x W) / P
        # F is focal length, P is pixel width, D is distance, W is width irl
        self.objects = {}
        index = 0
        if self.lens_type == LensType.SINGLE:
            for (x, y, w, h) in self.detected_objects:
                index += 1
                x1 = x + w
                y1 = y + h
                cv2.rectangle(
                    self.frame, (x, y), (x1, y1), Conf.CV_LINE_COLOR
                )
            if self.num_objects <= 1:
                for (x, y, w, h) in self.detected_objects:
                    self.objects[DistanceType.MAIN] = (
                        (self.focal_len * self.obj_width) / w
                    )
            else:
                self.logger.debug(
                    f"Several objects detected. Num: {self.num_objects}"
                )
        elif self.lens_type == LensType.DOUBLE:
            for (x, y, w, h) in self.detected_left:
                index += 1
                x1 = x + w
                y1 = y + h
                cv2.rectangle(
                    self.frame_left, (x, y), (x1, y1), Conf.CV_LINE_COLOR
                )
            for (x, y, w, h) in self.detected_right:
                index += 1
                x1 = x + w
                y1 = y + h
                cv2.rectangle(
                    self.frame_right, (x, y), (x1, y1), Conf.CV_LINE_COLOR
                )
            if self.num_left <= 1 and self.num_right <= 1:
                for (x, y, w, h) in self.detected_left:
                    self.objects[DistanceType.LEFT] = (
                        (self.focal_len * self.obj_width) / w
                    )
                for (x, y, w, h) in self.detected_right:
                    self.objects[DistanceType.RIGHT] = (
                        (self.focal_len * self.obj_width) / w
                    )
                if (
                        DistanceType.LEFT in self.objects
                        and DistanceType.RIGHT in self.objects
                ):
                    self.objects[DistanceType.MAIN] = (
                        (
                                self.objects[DistanceType.LEFT]
                                + self.objects[DistanceType.RIGHT]
                        ) / 2
                    )
            else:
                self.logger.debug(
                    "Several objects detected. "
                    f"Left: {self.num_left}. Right: {self.num_right}"
                )
        if self.objects != {}:
            self.logger.debug(f"detect_object: objects {self.objects}")
        else:
            self.logger.debug('detect_object: empty')

    def get_dual_image(self):
        self.midpoint = int(self.width / 2)
        self.frame_left = self.frame[0: self.height, 0: self.midpoint]
        self.frame_right = (
            self.frame[0: self.height, self.midpoint: self.width]
        )

    def calibrate(self):
        self.logger.debug("calibrate called")
        options = {'y': "yes", 'n': "no"}
        continue_calibrate = True
        while continue_calibrate:
            response = input(
                f"current profile: {self.profile}\n"
                "Enter:\n"
                "  - 0 to exit\n"
                "  - 1 to edit default\n"
                "  - 2 to chose a different profile\n"
            ).strip()
            if response == "0":
                continue_calibrate = False
            elif response == "1":
                profile = Conf.CS_DEFAULT
                print(
                    f"The current parameters for {profile} are:\n"
                    f"     Focal length --> "
                    f"{self.settings[profile][Conf.CS_FOCAL]}\n"
                    f"     Object width --> "
                    f"{self.settings[profile][Conf.CS_OBJ_WIDTH]}"
                )
                self.setup_profile(Conf.CS_DEFAULT)
                if self.profile != Conf.CS_DEFAULT:
                    print("Would you like to change your profile to default?")
                    response = get_specific_response(options)
                    if response == 'y':
                        self.profile = Conf.CS_DEFAULT
                        self.update_instance_settings()
            elif response == "2":
                for key in self.settings:
                    print(key)
                profile = input(
                    "Please enter a profile name from the list above or "
                    "enter a new setting name: "
                ).strip()
                if profile in self.settings:
                    print(
                        f"The current parameters for {profile} are:\n"
                        f"     Focal length --> "
                        f"{self.settings[profile][Conf.CS_FOCAL]}\n"
                        f"     Object width --> "
                        f"{self.settings[profile][Conf.CS_OBJ_WIDTH]}"
                    )
                    print("Would you like to alter the parameters?")
                    response = get_specific_response(options)
                    if response == "y":
                        self.setup_profile(profile)
                else:
                    alert = ""
                    while alert == "":
                        print(
                            f"You entered '{profile}' which does not exist. "
                            f"Are you sure you want to create a new profile?"
                        )
                        alert = get_specific_response(options)
                        if alert == "n":
                            print("Canceling operation")
                    if alert == "y":
                        self.setup_profile(profile)
                if profile != self.profile and profile in self.settings:
                    print(
                        "Would you like to switch to this profile? "
                    )
                    response = get_specific_response(options)
                    if response == 'y':
                        self.profile = profile
                        self.update_instance_settings()
        self.update_instance_settings()
        self.logger.debug(f"Calibrate exiting")

    def setup_profile(self, profile):
        self.logger.debug("setup_profile called")
        options = {'y': "yes", 'n': "no"}
        if profile not in self.settings:
            self.settings[profile] = {}
        if Conf.CS_LENS_TYPE in self.settings[profile]:
            if self.settings[profile][Conf.CS_LENS_TYPE] != self.lens_type.value:
                print(
                    f"The lens type of this profile is "
                    f"{self.settings[profile][Conf.CS_LENS_TYPE]}. "
                    f"Do you want to change it to {self.lens_type.value} "
                    f"which is the lens type of this camera"
                )
                response = get_specific_response(options)
                if response == 'y':
                    self.settings[profile][Conf.CS_LENS_TYPE] = self.lens_type.value
                else:
                    print("Canceling set up")
                    return
        else:
            self.settings[profile][Conf.CS_LENS_TYPE] = self.lens_type.value
        if Conf.CS_NEIGH not in self.settings[profile]:
            self.settings[profile][Conf.CS_NEIGH] = 4
        if Conf.CS_SCALE not in self.settings[profile]:
            self.settings[profile][Conf.CS_SCALE] = 1.405
        self.settings[profile][Conf.CS_OBJ_WIDTH] = get_float(
            "Enter object real world width: "
        )
        response = ""
        while response == "":
            response = input(
                "Would you like the program to calculate focal length or would "
                "you like to enter it manually? '1' for the program to "
                "calculate and '2' for manual: "
            ).strip()
            if response != '1' and response != '2':
                print(f"{response} is not a valid response!!!")
                response = ""
        if response == '1':
            # Calibrate detection ############################################
            print(
                "You now have the opportunity to calibrate the detection. "
                "Please calibrate the detection using the track bars then "
                "press any letter on the keyboard to continue."
            )
            do_calibration = True
            while do_calibration:
                self.ret, self.frame = self.cam.read()
                if self.lens_type == LensType.SINGLE:
                    gray_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                    detected_objects = Conf.CV_DETECTOR.detectMultiScale(
                        gray_frame,
                        self.settings[self.profile][Conf.CS_SCALE],
                        self.settings[self.profile][Conf.CS_NEIGH],
                    )
                    if detected_objects is not None:
                        for (x, y, w, h) in detected_objects:
                            x1 = x + w
                            y1 = y + h
                            cv2.rectangle(
                                self.frame,
                                (x, y),
                                (x1, y1),
                                Conf.CV_LINE_COLOR
                            )
                elif self.lens_type == LensType.DOUBLE:
                    self.get_dual_image()
                    gray_left = cv2.cvtColor(
                        self.frame_left, cv2.COLOR_BGR2GRAY
                    )
                    gray_right = cv2.cvtColor(
                        self.frame_right, cv2.COLOR_BGR2GRAY
                    )
                    detected_left = Conf.CV_DETECTOR.detectMultiScale(
                        gray_left,
                        self.settings[self.profile][Conf.CS_SCALE],
                        self.settings[self.profile][Conf.CS_NEIGH],
                    )
                    detected_right = Conf.CV_DETECTOR.detectMultiScale(
                        gray_right,
                        self.settings[self.profile][Conf.CS_SCALE],
                        self.settings[self.profile][Conf.CS_NEIGH],
                    )
                    if detected_left is not None:
                        for (x, y, w, h) in detected_left:
                            x1 = x + w
                            y1 = y + h
                            cv2.rectangle(
                                self.frame_left,
                                (x, y),
                                (x1, y1),
                                Conf.CV_LINE_COLOR
                            )
                    if detected_right is not None:
                        for (x, y, w, h) in detected_right:
                            x1 = x + w
                            y1 = y + h
                            cv2.rectangle(
                                self.frame_right,
                                (x, y),
                                (x1, y1),
                                Conf.CV_LINE_COLOR
                            )
                cv2.imshow(Conf.CV_WINDOW, self.frame)
                k = cv2.waitKey(1) & 0xFF
                if k != -1 and k != 255:
                    do_calibration = False
            # Calibrate focal length  #######################################
            # Formula: F = (P x  D) / W
            print(
                "\n"
                "To calculate the focal length of the camera the object must "
                "be placed at a known fixed distance from the camera."
            )
            distance = get_float(
                "Please enter the objects distance from the camera: "
            )
            print(
                "\n"
                "The program will now automatically detect the pixel size of "
                "the object. \nPress any key other than 'y' to cycle through "
                "all obtained sizes from the camera denoted by the bounding "
                "box (space recommended). \nOnce the detection is to your "
                "satisfaction please press 'y' to continue."
            )
            do_calibration = True
            while do_calibration:
                self.ret, self.frame = self.cam.read()
                if self.lens_type == LensType.SINGLE:
                    gray_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                    detected_objects = Conf.CV_DETECTOR.detectMultiScale(
                        gray_frame,
                        self.settings[self.profile][Conf.CS_SCALE],
                        self.settings[self.profile][Conf.CS_NEIGH],
                    )
                    if detected_objects is not None:
                        if len(detected_objects) == 1:
                            pixel_width = 0
                            for (x, y, w, h) in detected_objects:
                                x1 = x + w
                                y1 = y + h
                                pixel_width = w
                                cv2.rectangle(
                                    self.frame,
                                    (x, y),
                                    (x1, y1),
                                    Conf.CV_LINE_COLOR
                                )
                            cv2.imshow(Conf.CV_WINDOW, self.frame)
                            k = cv2.waitKey() & 0xFF
                            if k == ord('y'):
                                do_calibration = False
                                self.settings[profile][Conf.CS_FOCAL] = (
                                        (pixel_width * distance)
                                        /
                                        self.settings
                                        [profile][Conf.CS_OBJ_WIDTH]
                                )
                elif self.lens_type == LensType.DOUBLE:
                    self.get_dual_image()
                    gray_left = cv2.cvtColor(
                        self.frame_left, cv2.COLOR_BGR2GRAY
                    )
                    gray_right = cv2.cvtColor(
                        self.frame_right, cv2.COLOR_BGR2GRAY
                    )
                    detected_left = Conf.CV_DETECTOR.detectMultiScale(
                        gray_left,
                        self.settings[self.profile][Conf.CS_SCALE],
                        self.settings[self.profile][Conf.CS_NEIGH],
                    )
                    detected_right = Conf.CV_DETECTOR.detectMultiScale(
                        gray_right,
                        self.settings[self.profile][Conf.CS_SCALE],
                        self.settings[self.profile][Conf.CS_NEIGH],
                    )
                    if (
                            detected_left is not None
                            and detected_right is not None
                    ):
                        if (
                                len(detected_left) == len(detected_right)
                                and len(detected_left) == 1
                        ):
                            width_left = 0
                            width_right = 0
                            for (x, y, w, h) in detected_left:
                                x1 = x + w
                                y1 = y + h
                                width_left = w
                                cv2.rectangle(
                                    self.frame_left,
                                    (x, y),
                                    (x1, y1),
                                    Conf.CV_LINE_COLOR
                                )
                            for (x, y, w, h) in detected_right:
                                x1 = x + w
                                y1 = y + h
                                width_right = w
                                cv2.rectangle(
                                    self.frame_right,
                                    (x, y),
                                    (x1, y1),
                                    Conf.CV_LINE_COLOR
                                )
                            cv2.imshow(Conf.CV_WINDOW, self.frame)
                            k = cv2.waitKey() & 0xFF
                            if k == ord('y'):
                                do_calibration = False
                                self.settings[profile][Conf.CS_FOCAL_L] = (
                                        (width_left * distance)
                                        /
                                        self.settings
                                        [profile][Conf.CS_OBJ_WIDTH]
                                )
                                self.settings[profile][Conf.CS_FOCAL_R] = (
                                        (width_right * distance)
                                        /
                                        self.settings
                                        [profile][Conf.CS_OBJ_WIDTH]
                                )
        elif response == '2':
            self.settings[profile][Conf.CS_FOCAL] = get_float(
                "Enter focal length: "
            )

    def update_instance_settings(self):
        self.logger.debug("update_instance_settings called")
        self.focal_len = self.settings[self.profile][Conf.CS_FOCAL]
        self.obj_width = self.settings[self.profile][Conf.CS_OBJ_WIDTH]

    def set_scale(self, position):
        self.settings[self.profile][Conf.CS_SCALE] = 0.1 * position + 1.005

    def set_neigh(self, position):
        self.settings[self.profile][Conf.CS_NEIGH] = position

    def close(self):
        self.logger.info(
            f"Camera is closing after running for {pretty_time(self.start)} "
        )
        with open(Conf.CAM_SETTINGS_FILE, 'w') as file:
            json.dump(self.settings, file, indent=4)
        self.cam.release()
        cv2.destroyAllWindows()


def main():
    cam = Camera.get_inst(RobotType.SPIDER)
    cam.calibrate()
    cam.start_recognition()
    cam.close()


if __name__ == "__main__":
    main()

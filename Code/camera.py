"""
Kuwin Wyke
Midwestern State University
"""
import json
import logging
import os
import re
import threading
import time
import cv2
import numpy as np
is_rpi = False
if "raspberrypi" in os.uname():
    is_rpi = True
    from picamera import PiCamera
    from picamera.exc import PiCameraError
    from picamera.array import PiRGBArray

import log_set_up
from misc import manual_ender, get_float, get_specific_response, pretty_time
from config import Conf
from enums import RobotType, LensType, ObjDist, DurTypes
from variables import ExitControl


class Camera:
    _inst = {}
    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
    logger = logging.getLogger(Conf.LOG_CAM_NAME)

    @staticmethod
    def get_inst(
            cam_name, cam_num=0, lens_type=LensType.SINGLE,
            record=False, take_pic=False, disp_img=False
    ):
        with Conf.LOCK_CAM:
            if cam_name not in Camera._inst:
                Camera._inst[cam_name] = Camera(
                    cam_name, cam_num, lens_type, record, take_pic, disp_img
                )
        return Camera._inst[cam_name]

    def __init__(self, robot, cam_num, lens_type, record, take_pic, disp_img):
        self.main_logger.info(f"Camera: started on version {Conf.VERSION}")
        self.logger.info(
            f"Cam started on version {Conf.VERSION}:\n"
            f"- robot: {robot}\n"
            f"- cam_num: {cam_num}\n"
            f"- lens_type: {lens_type}\n"
            f"- record: {record}\n"
            f"- take_pic: {take_pic}\n"
            f"- Display image: {disp_img}"
        )
        self.start_time = time.time()
        self.lock = Conf.LOCK_CAM
        self.count = 0
        if lens_type != LensType.SINGLE and lens_type != LensType.DOUBLE:
            self.logger.exception(f"'{lens_type}' is not a valid lens type")
            self.main_logger.exception(
                f"Camera: crashed -- '{lens_type}' is not a valid lens type"
            )
            raise ValueError(f"'{lens_type}' is not a valid lens type")
        if robot != RobotType.HUMAN and robot != RobotType.SPIDER:
            self.logger.exception(f"'{robot}' is not a valid robot type")
            self.main_logger.exception(
                f"Camera: crashed -- '{robot}' is not a valid robot type"
            )
            raise ValueError(f"'{robot}' is not a valid robot type")

        self.disp_img = disp_img
        self.robot_type = robot
        self.robot = None
        if cam_num < 0:
            try:
                self.height = 480
                self.width = 640
                self.cam = PiCamera()
                self.cam.resolution = (self.width, self.height)
                self.cam.framerate = 32
                self.rawCapture = PiRGBArray(
                    self.cam, size=(self.width, self.height)
                )
                self.ret = True
                time.sleep(0.1)
            except PiCameraError:
                pass
        else:
            self.cam = cv2.VideoCapture(cam_num)
            self.ret, self.frame_pure = self.cam.read()
        if not self.ret:
            self.cam_num = -1
        else:
            self.cam_num = cam_num
        while not self.ret:
            if is_rpi and self.cam_num < 0:
                try:
                    self.cam = PiCamera()
                    self.height = 480
                    self.width = 640
                    self.cam.resolution = (self.width, self.height)
                    self.cam.framerate = 32
                    self.rawCapture = PiRGBArray(
                        self.cam, size=(self.width, self.height)
                    )
                    self.ret = True
                    time.sleep(0.1)
                except PiCameraError:
                    self.logger.debug(f"__inti__: Pi Cam not connected")
            else:
                self.cam = cv2.VideoCapture(self.cam_num)
                self.ret, self.frame_pure = self.cam.read()
            self.cam_num += 1
            if self.cam_num > 5:
                raise Exception("No viable camera found ")
        if self.cam_num != cam_num:
            self.logger.info(
                f"Cam num changed from {cam_num} to {self.cam_num} because"
                " original number did not have a camera associated with it"
            )
        self.lens_type = lens_type
        self.focal_len = None
        self.focal_len_l = None
        self.focal_len_r = None
        self.obj_width = None
        self.height, self.width, _ = self.frame_pure.shape
        self.midpoint = int(self.width / 2)
        if lens_type == LensType.DOUBLE:
            self.midpoint = int(self.width / 4)
            self.width = int(self.width / 2)
            self.get_dual_image()
        self.note_frame = np.zeros(
            [Conf.CV_NOTE_HEIGHT, self.width, 3], dtype=np.uint8
        )
        self.frame = self.frame_pure.copy()
        self.frame_full = np.vstack((self.frame, self.note_frame))
        self.write_note = True

        with open(Conf.CAM_SETTINGS_FILE) as file:
            self.settings = json.load(file)
        if lens_type == LensType.SINGLE:
            self.profile = Conf.CS_DEFAULT
        elif lens_type == LensType.DOUBLE:
            self.profile = Conf.CS_DEFAULT2
        if self.profile not in self.settings:
            setup_profile = True
            temp_disp = self.disp_img
            self.disp_img = True
            self.reset_profile(self.profile)
        else:
            setup_profile = False
        files = os.listdir(Conf.PIC_ROOT)
        if len(files) > 0:
            files = [int(f[:-4]) for f in files]
            files.sort()
            self.pic_num = files[-1] + 1
        else:
            self.pic_num = 0
        self.last_pic_time = 0
        self.take_pic = take_pic

        self.last_vid_write = 0
        frame_rate = 10
        self.vid_write_frequency = 1 / frame_rate
        self.record = record
        if record:
            self.logger.info("Recording active")
            height, width, _ = self.frame_full.shape
            self.video_writer = cv2.VideoWriter(
                Conf.CV_VIDEO_FILE,
                cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                frame_rate, (width, height)
            )

        self.obj_dist = {}
        self.reset_distances(True)
        self.last_non_search = time.time()
        self.note_dict = {}

        self.command = None
        self.num_objects = 0
        self.num_left = 0
        self.num_right = 0
        self.detected_objects = None
        self.detected_left = None
        self.detected_right = None
        self.is_detected_equal = True
        self.is_detected = False
        if disp_img:
            track_bar = Conf.CV_WINDOW
            track_bar_scale = 4
            track_bar_neigh = 4
            if self.profile in self.settings:
                if Conf.CS_SCALE in self.settings[self.profile]:
                    track_bar_scale = (
                            (
                                self.settings[self.profile][Conf.CS_SCALE]
                                - 1.005
                            )
                            / 0.1
                    )
                    track_bar_scale = int(f"{track_bar_scale: .0f}")
                if Conf.CS_NEIGH in self.settings[self.profile]:
                    track_bar_neigh = (
                        self.settings[self.profile][Conf.CS_NEIGH]
                    )
            cv2.namedWindow(Conf.CV_WINDOW)
            cv2.namedWindow(track_bar)
            cv2.createTrackbar(
                "scale", track_bar, track_bar_scale, 89, self.set_scale
            )
            cv2.createTrackbar(
                "min Neigh", track_bar, track_bar_neigh, 50, self.set_neigh
            )
        if setup_profile:
            self.setup_profile(self.profile)
            self.disp_img = temp_disp
            if not self.disp_img:
                cv2.destroyWindow(Conf.CV_WINDOW)
        self.update_instance_settings()

        self.logger.debug(
            f"Cam init ran in {pretty_time(self.start_time)}"
        )

    ##########################################################################
    # Main detection function. ###############################################
    ##########################################################################
    def start_recognition(self):
        self.logger.debug("start_recognition started")
        loop_dur = 0
        total_dur = time.time() - self.start_time
        threshold = Conf.LOOP_DUR_THRESHOLD / 1000
        while (
                self.settings[self.profile][Conf.CS_LENS_TYPE]
                != self.lens_type.value
        ):
            if not self.disp_img:
                self.main_logger.exception(
                    "Camera: Lens type of camera and settings progile do not "
                    "match but test env not active. Raising exception now."
                )
                self.logger.exception(
                    "Lens type of camera and settings profile do not match "
                    "but test env not active. Raising exception now."
                )
                raise Exception("ERROR: lens type error - start_recognition ")
            self.logger.info(
                "Lens type of camera and settings profile do not match. "
                "Please fix"
            )
            self.calibrate()
        if self.disp_img:
            support = threading.Thread(target=self.main_loop_support)
            support.start()
        while ExitControl.gen and ExitControl.cam:
            loop_start = time.time()
            self.get_frame()
            self.detect_object()
            note_x = Conf.CS_X_OFFSET
            note_y = Conf.CV_NOTE_HEIGHT - Conf.CS_Y_OFFSET
            self.note_dict[DurTypes.MAIN_DUR] = [
                pretty_time(total_dur, False), note_x, note_y
            ]
            note_y -= Conf.CS_Y_OFFSET
            self.note_dict[DurTypes.MAIN_LOOP] = [
                pretty_time(loop_dur, False), note_x, note_y
            ]

            if self.record:
                note_x = self.width - (Conf.CS_X_OFFSET * 10)
                note_y = Conf.CV_NOTE_HEIGHT - Conf.CS_Y_OFFSET
                text = "Recording"
                self.put_text(text, note_x, note_y)
                dur = time.time() - self.last_vid_write
                if dur > self.vid_write_frequency:
                    self.video_writer.write(self.frame_full)
                    self.logger.debug(
                        "start_recognition: Writing to video file"
                    )
            if self.take_pic:
                self.capture_picture(limit=True)
            if self.disp_img:
                self.show_frames()
            k = cv2.waitKey(50)
            if k == 27:
                ExitControl.gen = False

            loop_dur = time.time() - loop_start
            total_dur = time.time() - self.start_time
            if loop_dur < threshold:
                self.logger.debug(
                    f"Recognition loop ran in {pretty_time(loop_dur, False)}"
                )
                self.logger.debug(
                    f"Total runtime {pretty_time(total_dur, False)}"
                )
            else:
                self.logger.warning(
                    f"Recognition loop ran in {pretty_time(loop_dur, False)}"
                    f"\n----------------------------- "
                    f"This is greater than the threshold of "
                    f"{Conf.LOOP_DUR_THRESHOLD}ms"
                )

    def main_loop_support(self):
        start_time = time.time()
        time.sleep(.1)
        while ExitControl.gen and ExitControl.cam:
            loop_start_time = time.time()
            self.frame = self.frame_pure.copy()
            if self.num_objects == 1:
                for (x, y, w, h) in self.detected_objects:
                    x1 = x + w
                    y1 = y + h
                    with self.lock:
                        cv2.rectangle(
                            self.frame, (x, y), (x1, y1), Conf.CV_LINE_COLOR
                        )
                for (x, y, w, h) in self.detected_objects:
                    dist = (self.focal_len * self.obj_width) / w
                    check = self.obj_dist[ObjDist.AVG] - dist
                    if -Conf.DIST_DISCREPANCY < check < Conf.DIST_DISCREPANCY:
                        self.obj_dist[ObjDist.LIST].insert(0, dist)
                        self.obj_dist[ObjDist.SUM] += dist
                        self.obj_dist[ObjDist.COUNT] += 1
                        if (
                                self.obj_dist[ObjDist.COUNT]
                                > Conf.MEM_DIST_LIST_LEN
                        ):
                            num = self.obj_dist[ObjDist.LIST].pop()
                            self.obj_dist[ObjDist.SUM] -= num
                            self.obj_dist[ObjDist.COUNT] -= 1
                        self.obj_dist[ObjDist.AVG] = (
                                self.obj_dist[ObjDist.SUM]
                                / self.obj_dist[ObjDist.COUNT]
                        )
                        self.obj_dist[ObjDist.LAST_SEEN] = (
                            time.time()
                        )
                        self.obj_dist[ObjDist.IS_FOUND] = True
                        note_x = x
                        note_y = y - int(Conf.CS_Y_OFFSET / 2)
                        text = f"Distance: {self.obj_dist[ObjDist.AVG]:.2f}"
                        self.put_text(text, note_x, note_y)
                        center_point = x + (w / 2)
                        left_limit = self.midpoint - Conf.CS_MID_TOLERANCE
                        right_limit = self.midpoint + Conf.CS_MID_TOLERANCE
                        if center_point < left_limit:
                            pos = Conf.CMD_LEFT
                        elif center_point > right_limit:
                            pos = Conf.CMD_RIGHT
                        else:
                            pos = Conf.CONST_MIDDLE
                        self.obj_dist[ObjDist.LOCATION] = pos
                        note_y = y + h + Conf.CS_Y_OFFSET
                        text = f"Location: {self.obj_dist[ObjDist.LOCATION]}"
                        self.put_text(text, note_x, note_y)
                    else:
                        self.logger.debug(
                            f"main_loop_support: "
                            f"Major deviation in calculated.\n"
                            f"avg: "
                            f"{self.obj_dist[ObjDist.AVG]} vs dist: {dist}"
                        )
            else:
                if self.detected_objects is not None:
                    for (x, y, w, h) in self.detected_objects:
                        x1 = x + w
                        y1 = y + h
                        with self.lock:
                            cv2.rectangle(
                                self.frame, (x, y), (x1, y1),
                                Conf.CV_LINE_COLOR2
                            )
                self.logger.debug(
                    f"main_loop_support:Several objects detected. "
                    f"Num: {self.num_objects}"
                )
            note_x = Conf.CS_X_OFFSET
            note_y = Conf.CV_NOTE_HEIGHT - 3 * Conf.CS_Y_OFFSET
            self.note_dict[DurTypes.MAIN_SUP_DUR] = [
                pretty_time(start_time), note_x, note_y
            ]
            note_y -= Conf.CS_Y_OFFSET
            self.note_dict[DurTypes.MAIN_SUP_LOOP] = [
                pretty_time(loop_start_time), note_x, note_y
            ]
            if self.write_note:
                note_x = Conf.CS_X_OFFSET
                note_y = Conf.CS_Y_OFFSET
                text = time.strftime(Conf.FORMAT_DATE)
                self.put_text(text, note_x, note_y, frame=self.note_frame)

                if self.obj_dist[ObjDist.IS_FOUND]:
                    note_y += Conf.CS_Y_OFFSET
                    text = (
                        f"Distance "
                        f"{self.obj_dist[ObjDist.AVG]:.2f}"
                    )
                    self.put_text(text, note_x, note_y, frame=self.note_frame)
                    note_y += Conf.CS_Y_OFFSET
                    text = (
                        "Relative location in vision: "
                        f"{self.obj_dist[ObjDist.LOCATION]}"
                    )
                    self.put_text(text, note_x, note_y, frame=self.note_frame)
                else:
                    self.logger.debug("main_loop_support: Object not found")

                for key, [value, x, y] in self.note_dict.items():
                    text = f"{key}: {value}"
                    self.put_text(text, x, y, frame=self.note_frame)
                self.write_note = False
    ##########################################################################

    ##########################################################################
    # Main robot control function ############################################
    ##########################################################################
    def control_robot(self):
        # All relevant command numbers can be found in config.Conf
        # HUMANOID_FULL and SPIDER_FULL
        from robot_control import Robot
        self.logger.debug("control_robot: Started")
        self.robot = Robot.get_inst(self.robot_type)
        turning = False
        cmd_sent = None
        cmd_sent_time = 0
        wait_time = 0
        time.sleep(3)
        while ExitControl.gen and ExitControl.cam:
            success = False
            dur = time.time() - cmd_sent_time
            orig_wait_time = wait_time
            if self.obj_dist[ObjDist.IS_FOUND]:
                self.last_non_search = time.time()
                if turning:
                    self.robot.send_command(-1, auto=True)
                    wait_time = 0
                if dur > wait_time:
                    if (
                            Conf.KICK_DIST + Conf.KICK_RANGE
                            > self.obj_dist[ObjDist.AVG]
                            > Conf.KICK_DIST - Conf.KICK_RANGE
                    ):  # Within kick range
                        if self.robot_type == RobotType.HUMAN:
                            self.command = 26
                            wait_time = Conf.HUMANOID_FULL[self.command][1]
                        elif self.robot_type == RobotType.SPIDER:
                            self.command = 29
                            wait_time = Conf.SPIDER_FULL[self.command][1]
                        cmd_sent = Conf.CMD_KICK
                    elif (
                            self.obj_dist[ObjDist.AVG]
                            > Conf.KICK_DIST
                    ):  # Walk forward
                        if self.robot_type == RobotType.HUMAN:
                            self.command = 15
                            wait_time = Conf.HUMANOID_FULL[self.command][1]
                        elif self.robot_type == RobotType.SPIDER:
                            self.command = 5
                            wait_time = Conf.SPIDER_FULL[self.command][1]
                        cmd_sent = Conf.CMD_FORWARD
                    else:  # Walk backward
                        if self.robot_type == RobotType.HUMAN:
                            self.command = 16
                            wait_time = Conf.HUMANOID_FULL[self.command][1]
                        elif self.robot_type == RobotType.SPIDER:
                            self.command = 6
                            wait_time = Conf.SPIDER_FULL[self.command][1]
                        cmd_sent = Conf.CMD_BACKWARD
                    cmd_sent_time = time.time()
                    success = self.robot.send_command(self.command, auto=True)
            else:  # Search for object
                non_search_dur = time.time() - self.last_non_search
                if non_search_dur < Conf.MAX_SEARCH_DUR:
                    turning = (
                            cmd_sent == Conf.CMD_LEFT
                            or cmd_sent == Conf.CMD_RIGHT
                    )
                    if not turning or turning and non_search_dur > wait_time:
                        turn_direction = (
                            self.obj_dist[ObjDist.LOCATION]
                        )
                        if turn_direction == Conf.CMD_LEFT:
                            if self.robot_type == RobotType.HUMAN:
                                self.command = 19
                                wait_time = (
                                    Conf.HUMANOID_FULL[self.command][1]
                                )
                            elif self.robot_type == RobotType.SPIDER:
                                self.command = 7
                                wait_time = Conf.SPIDER_FULL[self.command][1]
                            cmd_sent = Conf.CMD_LEFT
                        else:  # Turn right
                            if self.robot_type == RobotType.HUMAN:
                                self.command = 20  # Conf.HUMANOID_MOTION
                                wait_time = (
                                    Conf.HUMANOID_FULL[self.command][1]
                                )
                            elif self.robot_type == RobotType.SPIDER:
                                self.command = 8  # Conf.SPIDER_FULL
                                wait_time = Conf.SPIDER_FULL[self.command][1]
                            cmd_sent = Conf.CMD_RIGHT
                        success = self.robot.send_command(
                            self.command, auto=True
                        )
                        cmd_sent_time = time.time()
                else:
                    self.logger.warning(
                        "Object not found in "
                        f"{pretty_time(non_search_dur, is_raw=False)}"
                        " and robot has stopped searching"
                    )
            if success and dur > orig_wait_time:
                self.logger.info(f"control_robot: Command sent: {cmd_sent}")
            time.sleep(2)
    ##########################################################################

    def show_frames(self):
        with self.lock:
            self.frame_full = np.vstack((self.frame, self.note_frame))
            cv2.imshow(Conf.CV_WINDOW, self.frame_full)

    def get_frame(self, with_lock=True):
        def sub_get_frame():
            if self.cam_num < 0:
                self.cam.capture(
                    self.rawCapture, format="bgr", use_video_port=True
                )
                self.frame_pure = self.rawCapture.array
                self.ret = True
            else:
                self.ret, self.frame_pure = self.cam.read()
            if self.lens_type == LensType.DOUBLE:
                self.get_dual_image()
            self.note_frame = np.zeros(
                [Conf.CV_NOTE_HEIGHT, self.width, 3], dtype=np.uint8
            )
            self.write_note = True

        if with_lock:
            with self.lock:
                sub_get_frame()
        else:
            sub_get_frame()

    def detect_object(self):
        gray_frame = cv2.cvtColor(self.frame_pure, cv2.COLOR_BGR2GRAY)
        self.detected_objects = Conf.CV_DETECTOR.detectMultiScale(
            gray_frame,
            self.settings[self.profile][Conf.CS_SCALE],
            self.settings[self.profile][Conf.CS_NEIGH],
        )
        if self.detected_objects is not None:
            self.num_objects = len(self.detected_objects)
        else:
            self.num_objects = 0

        dur = (
            time.time() - self.obj_dist[ObjDist.LAST_SEEN]
        )
        if dur > Conf.MAX_LAST_SEEN:
            self.reset_distances()

    def get_dual_image(self):
        height = self.height
        end = self.width * 2
        self.frame_pure = self.frame_pure[0: height, self.width: end]

    def reset_distances(self, full_reset=False):
        self.obj_dist[ObjDist.AVG] = 0.0
        self.obj_dist[ObjDist.SUM] = 0.0
        self.obj_dist[ObjDist.COUNT] = 0
        self.obj_dist[ObjDist.IS_FOUND] = False
        self.obj_dist[ObjDist.LIST] = []
        if full_reset:
            self.obj_dist[ObjDist.LAST_SEEN] = 0.0

    def reset_profile(self, profile):
        self.settings[profile] = {}
        self.settings[profile][Conf.CS_NEIGH] = 3
        self.settings[profile][Conf.CS_SCALE] = 1.305
        self.settings[profile][Conf.CS_OBJ_WIDTH] = 2.56
        self.settings[profile][Conf.CS_LENS_TYPE] = self.lens_type.value
        self.settings[profile][Conf.CS_FOCAL_R] = 1
        self.settings[profile][Conf.CS_FOCAL_L] = 1
        self.settings[profile][Conf.CS_FOCAL] = 1

    def calibrate(self):
        self.logger.debug("calibrate called")
        if not self.disp_img:
            self.logger.exception("Can only calibrate when display enabled")
            return
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
                if (
                        self.profile != Conf.CS_DEFAULT
                        or self.profile != Conf.CS_DEFAULT2
                ):
                    print("Would you like to change your profile to default?")
                    response = get_specific_response(options)
                    if response == 'y':
                        profile = Conf.CS_DEFAULT
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
        self.logger.debug(f"setup_profile called for profile: {profile}")
        if not self.disp_img:
            self.logger.exception("Can only setup profile in testing mode")
            return
        options = {'y': "yes", 'n': "no"}
        if profile not in self.settings:
            self.settings[profile] = {}
        if Conf.CS_LENS_TYPE in self.settings[profile]:
            if (
                    self.settings[profile][Conf.CS_LENS_TYPE]
                    != self.lens_type.value
            ):
                print(
                    f"The lens type of this profile is "
                    f"{self.settings[profile][Conf.CS_LENS_TYPE]}. "
                    f"Do you want to change it to {self.lens_type.value} "
                    f"which is the lens type of this camera"
                )
                response = get_specific_response(options)
                if response == 'y':
                    self.settings[profile][Conf.CS_LENS_TYPE] = (
                        self.lens_type.value
                    )
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
                "Would you like the program to calculate focal length or "
                "would you like to enter it manually? '1' for the program to "
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
                self.get_frame(with_lock=False)
                gray_frame = cv2.cvtColor(self.frame_pure, cv2.COLOR_BGR2GRAY)
                detected_objects = Conf.CV_DETECTOR.detectMultiScale(
                    gray_frame,
                    self.settings[self.profile][Conf.CS_SCALE],
                    self.settings[self.profile][Conf.CS_NEIGH],
                )
                for (x, y, w, h) in detected_objects:
                    x1 = x + w
                    y1 = y + h
                    pixel_width = w
                    cv2.rectangle(
                        self.frame_pure,
                        (x, y),
                        (x1, y1),
                        Conf.CV_LINE_COLOR
                    )
                cv2.imshow(Conf.CV_WINDOW, self.frame_pure)
                k = cv2.waitKey(1) & 0xFF
                if k != -1 and k != 255 and len(detected_objects):
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
            self.settings[profile][Conf.CS_FOCAL] = (
                    (pixel_width * distance)
                    / self.settings[profile][Conf.CS_OBJ_WIDTH]
            )
            print(
                "Calculated focal length "
                f"= {self.settings[profile][Conf.CS_FOCAL]}"
            )
        elif response == '2':
            self.settings[profile][Conf.CS_FOCAL] = get_float(
                "Enter focal length: "
            )

    def capture_picture(self, limit=False):
        if limit:
            dur = time.time() - self.last_pic_time
            if dur < Conf.FREQUENCY_PIC:
                return

        cv2.imwrite(f"{Conf.PIC_ROOT}{self.pic_num}.jpg", self.frame_pure)
        self.logger.debug(
            f"capture_picture: Photo taken with name {self.pic_num}.jpg"
        )
        self.pic_num += 1
        self.last_pic_time = time.time()

    def update_instance_settings(self):
        self.logger.debug("update_instance_settings called")
        self.focal_len = self.settings[self.profile][Conf.CS_FOCAL]
        self.obj_width = self.settings[self.profile][Conf.CS_OBJ_WIDTH]

    def set_scale(self, position):
        self.settings[self.profile][Conf.CS_SCALE] = 0.1 * position + 1.005

    def set_neigh(self, position):
        self.settings[self.profile][Conf.CS_NEIGH] = position

    def put_text(self, text, x, y, *, frame=None, color=Conf.CV_TEXT_COLOR):
        with self.lock:
            if frame is None:
                frame = self.frame
            cv2.putText(
                frame,
                text,
                (x, y),
                Conf.CV_FONT,
                Conf.CV_FONT_SCALE,
                color,
                Conf.CV_THICKNESS,
                Conf.CV_LINE
            )

    def close(self):
        self.main_logger.info(
            "Camera: closing after running for "
            f"{pretty_time(self.start_time)}"
        )
        self.logger.info(
            "Camera: closing after running for "
            f"{pretty_time(self.start_time)}\n"
        )
        with open(Conf.CAM_SETTINGS_FILE, 'w') as file:
            json.dump(self.settings, file, indent=4)
        self.cam.release()
        cv2.destroyAllWindows()
        ExitControl.cam = False


def independent_test():
    ender = threading.Thread(target=manual_ender, daemon=True)
    # Don't use ender if you need to use terminal
    ender.start()
    cam = Camera.get_inst(
        RobotType.SPIDER,
        cam_num=2,
        lens_type=LensType.DOUBLE,
        # record=True,
        # take_pic=True,
        disp_img=True
    )
    # cam.calibrate()
    cam.start_recognition()
    cam.close()


if __name__ == "__main__":
    independent_test()

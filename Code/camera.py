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
from variables import ExitControl, HeartBeats


class Camera:
    # TODO: set up calibration in OpenCV
    #   * Currently default values are set for focus, object width ect.
    #   -> Redo main loop
    #   -> Set up calibration
    _inst = {}
    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
    logger = logging.getLogger(Conf.LOG_CAM_NAME)

    @staticmethod
    def get_inst(cam_name, cam_num=-1, disp=False, record=False, take_pic=False):
        with Conf.LOCK_CLASS:
            if cam_name not in Camera._inst:
                Camera._inst[cam_name] = Camera(
                    cam_name, cam_num, disp, record, take_pic
                )
        return Camera._inst[cam_name]

    def __init__(self, robot, cam_num, disp, record, take_pic):
        self.main_logger.info(f"Camera: started on version {Conf.VERSION}")
        self.logger.info(
            f"Cam started on version {Conf.VERSION}:\n"
            f"- robot: {robot}\n"
            f"- cam_num: {cam_num}\n"
            f"- display: {disp}\n"
            f"- record: {record}\n"
            f"- take_pic: {take_pic}\n"
        )
        self.start_time = time.time()
        self.lock = Conf.LOCK_CAM
        self.lock_detect = threading.Lock()
        self.count = 0
        self.is_connected = False
        if robot != RobotType.HUMAN and robot != RobotType.SPIDER:
            self.logger.exception(f"'{robot}' is not a valid robot type")
            self.main_logger.exception(
                f"Camera: crashed -- '{robot}' is not a valid robot type"
            )
            ExitControl.cam = False

        self.robot_type = robot
        self.robot = None
        self.cam_num = cam_num
        self.disp = disp
        self.frame = None
        self.width = self.height = 6
        self.is_pi_cam = False
        self.ret = False
        if cam_num < 0:
            if is_rpi:
                try:
                    self.height = 480
                    self.width = 640
                    self.cam = PiCamera()
                    self.cam.resolution = (self.width, self.height)
                    self.get_frame()
                    self.is_pi_cam = True
                    self.ret = True
                    self.is_connected = True
                except PiCameraError:
                    self.logger.exception("Tried to start pi cam but failed")
        else:
            try:
                self.cam = cv2.VideoCapture(cam_num)
                self.ret, self.frame = self.cam.read()
                self.height, self.width, _ = self.frame.shape
                self.is_pi_cam = False
                self.is_connected = True
            except AttributeError:
                pass
        if not self.ret:
            if is_rpi:
                self.cam_num = -2
            else:
                self.cam_num = -1
        while not self.ret and ExitControl.cam:
            self.cam_num += 1
            if is_rpi and self.cam_num < 0:
                try:
                    self.cam = PiCamera()
                    self.height = 480
                    self.width = 640
                    self.cam.resolution = (self.width, self.height)
                    self.get_frame()
                    self.is_pi_cam = True
                    self.ret = True
                    self.is_connected = True
                except PiCameraError:
                    pass
            else:
                try:
                    self.cam = cv2.VideoCapture(self.cam_num)
                    self.logger.debug(f"trying cv2 cam({self.cam_num}) now")
                    self.ret, self.frame = self.cam.read()
                    self.height, self.width, _ = self.frame.shape
                    self.is_pi_cam = False
                    self.is_connected = True
                    self.logger.debug(f"success cv2 cam({self.cam_num}) now")
                except AttributeError:
                    pass
            if self.cam_num > 5:
                self.logger.exception("No viable camera found")
                self.main_logger.exception(
                    "Camera: crashed -- No viable camera found"
                )
                self.is_connected = False
                ExitControl.cam = False
        if self.cam_num != cam_num:
            self.logger.info(
                f"Cam num changed from {cam_num} to {self.cam_num} because"
                " original number did not have a camera associated with it"
            )
        self.note_frame = np.zeros(
            [Conf.CV_NOTE_HEIGHT, self.width, 3], dtype=np.uint8
        )
        if self.is_connected:
            self.midpoint = int(self.width / 2)
            self.frame_full = np.vstack((self.frame, self.note_frame))
        else:
            self.frame = np.zeros([640, 640, 3], dtype=np.uint8)
            self.frame_full = self.frame.copy()
        self.focal_len = None
        self.obj_width = None
        self.write_note = True

        with open(Conf.CAM_SETTINGS_FILE) as file:
            self.settings = json.load(file)
        if self.is_pi_cam:
            self.profile = Conf.CS_DEFAULT
        else:
            self.profile = Conf.CS_DEFAULT1
        if self.profile in self.settings:
            self.is_profile_setup = True
        else:
            self.is_profile_setup = False
            self.reset_profile(self.profile)
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

        self.obj_dist = {}
        self.reset_distances(True)
        self.last_non_search = time.time()

        self.command = None
        self.num_objects = 0
        self.detected_objects = None
        self.update_instance_settings()
        self.main_loop_dur = 0
        self.get_frame_time = 0
        self.left_limit = self.midpoint - Conf.CS_MID_TOLERANCE
        self.right_limit = self.midpoint + Conf.CS_MID_TOLERANCE

        # This property will be used to pass actions from main recognition
        # loop to robot control loop
        self.action_request = ""

        self.logger.info(
            f"Cam init ran in {pretty_time(self.start_time)}"
        )

    ##########################################################################
    # Main detection function. ###############################################
    ##########################################################################
    def start_recognition(self):
        if not self.is_connected:
            self.logger.debug(
                "Camera recognition could not be started as camera is not "
                "connected"
            )
            self.is_profile_setup = True
            return
        self.logger.debug("start_recognition started")
        if not self.is_profile_setup:
            self.logger.debug("start_recognition: profile has to be set up")
            self.calibrate()
            self.is_profile_setup = True
        auto_thread = threading.Thread(target=self.control_robot)
        auto_thread.start()
        total_dur = time.time() - self.start_time
        threshold = Conf.LOOP_DUR_THRESHOLD / 1000
        while ExitControl.gen and ExitControl.cam:
            loop_start = time.time()
            self.get_frame()
            with self.lock_detect:
                self.detect_object()

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
                        if center_point < self.left_limit:
                            pos = Conf.CMD_LEFT
                        elif center_point > self.right_limit:
                            pos = Conf.CMD_RIGHT
                        else:
                            pos = Conf.CONST_MIDDLE
                        self.obj_dist[ObjDist.LOCATION] = pos
                        note_y = y + h + Conf.CS_Y_OFFSET
                        text = f"Location: {self.obj_dist[ObjDist.LOCATION]}"
                        self.put_text(text, note_x, note_y)
                    else:
                        self.logger.exception(
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

            ##################################################################
            # Place notes in openCV note window  #############################
            ##################################################################
            if self.disp:
                self.note_frame = np.zeros(
                    [Conf.CV_NOTE_HEIGHT, self.width, 3], dtype=np.uint8
                )
                note_x = Conf.CS_X_OFFSET
                note_y = Conf.CV_NOTE_HEIGHT - Conf.CS_Y_OFFSET
                self.put_text(
                    f"Main loop total time = {pretty_time(total_dur, False)}",
                    x=note_x, y=note_y, frame=self.note_frame
                )
                note_y -= Conf.CS_Y_OFFSET
                self.put_text(
                    "Main loop time = "
                    f"{pretty_time(self.main_loop_dur, False)}",
                    x=note_x, y=note_y, frame=self.note_frame
                )
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

                if self.record:
                    note_x = self.width - (Conf.CS_X_OFFSET * 10)
                    note_y = Conf.CV_NOTE_HEIGHT - Conf.CS_Y_OFFSET
                    text = "Recording"
                    self.put_text(text, note_x, note_y, frame=self.note_frame)
                    dur = time.time() - self.last_vid_write
                    if dur > self.vid_write_frequency:
                        self.video_writer.write(self.frame_full)
                        self.logger.debug(
                            "start_recognition: Writing to video file"
                        )

                if self.take_pic:
                    self.capture_picture(limit=True)

                self.frame_full = np.vstack((self.frame, self.note_frame))
                cv2.imshow(Conf.CV_WINDOW, self.frame_full)
                k = cv2.waitKey(1)
                if k == 27 or k == Conf.CMD_CV_EXIT or k == Conf.CMD_CV_EXIT1:
                    ExitControl.cam = ExitControl.gen = False
                    cv2.destroyAllWindows()
                elif k == Conf.CMD_CV_STOP or k == Conf.CMD_CV_STOP1:
                    self.action_request = Conf.CMD_STOP
                elif k == Conf.CMD_CV_DANCE:
                    self.action_request = Conf.CMD_DANCE
                elif k == Conf.CMD_CV_KICK:
                    self.action_request = Conf.CMD_KICK
                elif k == Conf.CMD_CV_FORWARD:
                    self.action_request = Conf.CMD_FORWARD
                elif k == Conf.CMD_CV_BACKWARD:
                    self.action_request = Conf.CMD_BACKWARD
                elif k == Conf.CMD_CV_LEFT:
                    self.action_request = Conf.CMD_LEFT
                elif k == Conf.CMD_CV_RIGHT:
                    self.action_request = Conf.CMD_RIGHT
                elif k == Conf.CMD_CV_HEAD_UP:
                    self.action_request = Conf.CMD_RH_UP
                elif k == Conf.CMD_CV_HEAD_DOWN:
                    self.action_request = Conf.CMD_RH_DOWN
                elif k == Conf.CMD_CV_HEAD_LEFT:
                    self.action_request = Conf.CMD_RH_LEFT
                elif k == Conf.CMD_CV_HEAD_RIGHT:
                    self.action_request = Conf.CMD_RH_RIGHT
                elif k == Conf.CMD_CV_HEAD_DELTA_P:
                    self.action_request = Conf.CMD_CV_HEAD_DELTA_P
                elif k == Conf.CMD_CV_HEAD_DELTA_M:
                    self.action_request = Conf.CMD_CV_HEAD_DELTA_M
                elif k == Conf.CMD_CV_DUMP_CAM:
                    self.action_request = Conf.CMD_VARS2
                elif k == Conf.CMD_CV_DUMP_ROBOT:
                    self.action_request = Conf.CMD_VARS
                elif k == Conf.CMD_CV_DUMP_CMD:
                    self.action_request = Conf.CMD_VARS1
            ##################################################################
            self.main_loop_dur = time.time() - loop_start
            total_dur = time.time() - self.start_time
            HeartBeats.cam = time.time()
            if self.main_loop_dur < threshold:
                self.logger.debug(
                    f"Recognition loop ran in {pretty_time(self.main_loop_dur, False)}"
                )
                self.logger.debug(
                    f"Total runtime {pretty_time(total_dur, False)}"
                )
            else:
                self.logger.debug(
                    f"Recognition loop ran in {pretty_time(self.main_loop_dur, False)}"
                    f"\n----------------------------- "
                    f"This is greater than the threshold of "
                    f"{Conf.LOOP_DUR_THRESHOLD}ms"
                )
    ##########################################################################

    ##########################################################################
    # Main robot control function ############################################
    ##########################################################################
    def control_robot(self):
        # All relevant command numbers can be found in config.Conf
        # HUMANOID_FULL and SPIDER_FULL
        if not self.is_connected:
            self.logger.debug(
                "Robot control could not be started as camera is not "
                "connected"
            )
            return
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
                    self.rbt_head_search()
                else:
                    self.logger.warning(
                        "Object not found in "
                        f"{pretty_time(non_search_dur, is_raw=False)}"
                        " and robot has stopped searching"
                    )
            if success and dur > orig_wait_time:
                self.logger.info(f"control_robot: Command sent: {cmd_sent}")

            if (
                    self.action_request == Conf.CMD_CV_HEAD_UP or
                    self.action_request == Conf.CMD_CV_HEAD_DOWN or
                    self.action_request == Conf.CMD_CV_HEAD_LEFT or
                    self.action_request == Conf.CMD_CV_HEAD_RIGHT
            ):
                self.robot.send_head_command(self.action_request)
            elif self.action_request == Conf.CMD_CV_HEAD_DELTA_P:
                self.robot.head_delta_theta += 5
            elif self.action_request == Conf.CMD_CV_HEAD_DELTA_M:
                self.robot.head_delta_theta -= 5
            elif self.action_request == Conf.CMD_VARS:
                self.robot.dump_status()
            elif self.action_request == Conf.CMD_VARS1:
                self.robot.dump_conf()
            elif self.action_request == Conf.CMD_VARS2:
                self.dump_status()
            elif self.action_request != "" :
                self.robot.send_command(self.action_request)

            if self.robot.cam_request == Conf.CMD_VARS2:
                self.dump_status()
            elif self.action_request != "":
                temp = (
                    "control_robot: current action_request before erasing "
                    f"--> {self.action_request}"
                )
                print(temp)
                self.action_request = ""

            if self.robot.cam_request != "":
                self.robot.cam_request = ""

            time.sleep(1)

    def rbt_head_search(self):
        self.robot.send_head_command(
            Conf.ROBOT_HEAD_SET_U_D, pos=Conf.RBT_MIN_HEAD_FORWARD, auto=True
        )
        while not self.obj_dist[ObjDist.IS_FOUND]:
            self.robot.send_head_command(Conf.CMD_RH_UP, auto=True)
            time.sleep(Conf.SEARCH_REST)
            if self.robot.servo_posUD >= Conf.RBT_MAX_HEAD_BACK:
                break
    ##########################################################################

    def get_frame(self):
        if not self.is_connected:
            self.logger.debug(
                "Camera could not get frame as camera is not connected"
            )
            return
        start = time.time()
        with self.lock:
            if self.cam_num < 0:
                rawCapture = PiRGBArray(
                    self.cam, size=(self.width, self.height)
                )
                self.cam.capture(
                    rawCapture, format="bgr", use_video_port=True
                )
                self.frame = rawCapture.array
                self.ret = True
            else:
                self.ret, self.frame = self.cam.read()
        self.get_frame_time = time.time() - start

    def detect_object(self):
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

        dur = (
            time.time() - self.obj_dist[ObjDist.LAST_SEEN]
        )
        if dur > Conf.MAX_LAST_SEEN:
            self.reset_distances()

    def reset_distances(self, full_reset=False):
        self.obj_dist[ObjDist.AVG] = 0.0
        self.obj_dist[ObjDist.LOCATION] = "N/A"
        self.obj_dist[ObjDist.SUM] = 0.0
        self.obj_dist[ObjDist.COUNT] = 0
        self.obj_dist[ObjDist.IS_FOUND] = False
        self.obj_dist[ObjDist.LIST] = []
        if full_reset:
            self.obj_dist[ObjDist.LAST_SEEN] = 0.0

    def reset_profile(self, profile):
        # TODO: Add option for if it is a rpi cam
        #   -> save camera Brightness
        #   -> save camera Contrast
        #   -> save camera ISO
        self.settings[profile] = {}
        self.settings[profile][Conf.CS_NEIGH] = 3
        self.settings[profile][Conf.CS_SCALE] = 1.305
        self.settings[profile][Conf.CS_OBJ_WIDTH] = 2.56
        self.settings[profile][Conf.CS_FOCAL] = 1
        if self.is_pi_cam:
            self.settings[profile][Conf.CS_IS_PI_CAM] = True
        else:
            self.settings[profile][Conf.CS_IS_PI_CAM] = False

    def calibrate(self):
        self.logger.debug("calibrate called")
        options = {'y': "yes", 'n': "no"}
        continue_calibrate = True
        while ExitControl.gen and ExitControl.cam and continue_calibrate:
            response = input(
                f"current profile: {self.profile}\n"
                "Enter:\n"
                "  - 0 to exit\n"
                "  - 1 to edit current profile\n"
                "  - 2 to chose a different profile\n"
            ).strip()
            if response == "0":
                continue_calibrate = False
            elif response == "1":
                print(
                    f"The current parameters for {self.profile} are:\n"
                    f"     Focal length --> "
                    f"{self.settings[self.profile][Conf.CS_FOCAL]}\n"
                    f"     Object width --> "
                    f"{self.settings[self.profile][Conf.CS_OBJ_WIDTH]}"
                )
                self.setup_profile(self.profile)
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
                    while ExitControl.gen and ExitControl.cam and alert == "":
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
        self.logger.debug(f"Calibrate exiting")

    def setup_profile(self, profile):
        self.logger.debug(f"setup_profile called for profile: {profile}")
        if profile not in self.settings:
            self.settings[profile] = {}
        if Conf.CS_NEIGH not in self.settings[profile]:
            self.settings[profile][Conf.CS_NEIGH] = 4
        if Conf.CS_SCALE not in self.settings[profile]:
            self.settings[profile][Conf.CS_SCALE] = 1.305
        self.settings[profile][Conf.CS_OBJ_WIDTH] = get_float(
            "Enter object real world width: "
        )
        response = ""
        while ExitControl.gen and ExitControl.cam and response == "":
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
            while ExitControl.gen and ExitControl.cam and do_calibration:
                self.get_frame()
                self.detect_object()
                for (x, y, w, h) in self.detected_objects:
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
                k = cv2.waitKey(1) & 0xFF
                if k == 27:
                    self.logger.debug("setup_profile: Exiting camera (esc)")
                    ExitControl.cam = False
                    return
                elif k != -1 and k != 255 and len(self.detected_objects):
                    do_calibration = False
            # Calibrate focal length  ########################################
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
        self.update_instance_settings()

    def capture_picture(self, limit=False):
        if limit:
            dur = time.time() - self.last_pic_time
            if dur < Conf.FREQUENCY_PIC:
                return

        cv2.imwrite(f"{Conf.PIC_ROOT}{self.pic_num}.jpg", self.frame)
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
        position = int(position)
        with self.lock_detect:
            self.settings[self.profile][Conf.CS_SCALE] = 0.1 * position + 1.005

    def set_neigh(self, position):
        position = int(position)
        self.settings[self.profile][Conf.CS_NEIGH] = position

    def set_brightness(self, position):
        if self.is_pi_cam:
            self.cam.brightness = int(position)
        else:
            self.logger.warning(
                "Brightness adjustment attempted on pi cam but not currently "
                f"using Pi Cam. cam_num={self.cam_num}"
            )

    def set_contrast(self, position):
        if self.is_pi_cam:
            self.cam.contrast = int(position)
        else:
            self.logger.warning(
                "Contrast adjustment attempted on pi cam but not currently "
                f"using Pi Cam. cam_num={self.cam_num}"
            )

    def set_iso(self, position):
        if self.is_pi_cam:
            self.cam.iso = int(position)
        else:
            self.logger.warning(
                "ISO adjustment attempted on pi cam but not currently "
                f"using Pi Cam. cam_num={self.cam_num}"
            )

    def put_text(
            self, text, x, y, *, frame=None, color=Conf.CV_TEXT_COLOR, scale=1
    ):
        with self.lock:
            if frame is None:
                frame = self.frame
            cv2.putText(
                frame,
                text,
                (x, y),
                Conf.CV_FONT,
                Conf.CV_FONT_SCALE * scale,
                color,
                Conf.CV_THICKNESS,
                Conf.CV_LINE
            )

    def dump_status(self):
        # This method is used to get the current status of all the
        # properties of the camera
        print(f"current properties:")
        properties = vars(self)
        for key in properties:
            print(f"property: {key} --> {properties[key]}")
            if type(properties[key]) is list or type(properties[key]) is dict:
                print()

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
        if self.cam_num < 0:
            self.cam.close()
        else:
            self.cam.release()
        cv2.destroyAllWindows()
        ExitControl.cam = False

    @property
    def inst(self):
        return self._inst


def independent_test():
    ender = threading.Thread(target=manual_ender, daemon=True)
    # Don't use ender if you need to use terminal
    ender.start()
    cam = Camera.get_inst(
        RobotType.SPIDER,
        cam_num=2,
        # record=True,
        # take_pic=True,
    )
    # cam.calibrate()
    cam.start_recognition()
    cam.close()


if __name__ == "__main__":
    independent_test()

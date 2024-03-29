import ast
import csv
import os
import random
import re

import pygame
import numpy as np

from config import Conf, GS
from controls import Controllers
from variables import Gen, ExitCtr, Frames, Sprites, DoFlag
from sim_objects import Robot, Ball, Goal, Score, SysInfo
from config import FrameStepReturn as fsr
X = Conf.X
Y = Conf.Y


class SimMaster:
    def __init__(self, index=-1, algorithm=GS.TYPE_NET):
        self.index = index  # Used to denote process instance
        self.initialized = False  # Used to determine if first call or not

        self.robots = []  # To be used later to control multiple robots
        self.robot = None  # Used to control first robot
        self.balls = []
        self.ball = None
        self.goals = []

        self.controller = None
        self.clock = None
        self.score = None
        self.sys_info = None
        self.rect = None
        self.num_reset = -1

        self.start_robot = None
        self.start_ball = None

        self.robot_xy = []
        self.ball_xy = []
        self.recorded_times = []
        self.pos_offset = Conf.RBT_SIZE[0]

        # Record information for later benchmarking neural net against "math"
        self.game_records = [
            (
                GS.ROBOT_START, GS.BALL_START,
                GS.TIME_TO_SCORE, GS.SIDE_SCORE, GS.METHOD
            )
        ]
        self.good_data_file = f"{Conf.CSV_FOLDER}/good_{algorithm}{index}.csv"
        self.bad_data_file = f"{Conf.CSV_FOLDER}/bad_{algorithm}{index}.csv"

        self.net = {
            Conf.DIRECTION: "",
            Conf.THETA: 0,
            Conf.DIST: 0,
            Conf.KICK: 0,
            Conf.CONT: 0,
        }
        self.algorithm = algorithm
        self.ball_bounce_x = 0
        self.is_goal_scored = False
        self.is_accurate_sent = False

        if len(self.robot_xy) != len(self.ball_xy):
            raise IndexError("None matching data set for ball and robot pos")

    def _init(self):
        if self.initialized:  # If already initialize exit
            return
        self.initialized = True
        pygame.init()

        # Set up simulation window
        height = Conf.HEIGHT + Conf.PADDING
        width = Conf.WIDTH + Conf.PADDING
        Gen.screen = pygame.display.set_mode((width, height))
        Gen.screen.fill(Conf.WHITE)

        # Field border rectangle dimensions
        self.rect = (Conf.ORIGIN[X], Conf.ORIGIN[Y], Conf.WIDTH, Conf.HEIGHT)

        # Create all simulation objects
        self.robots = [Robot(side=Conf.LEFT)]
        self.robot = self.robots[0]
        self.balls = [Ball(master=self)]
        self.ball = self.balls[0]
        self.goals = [Goal(Conf.LEFT), Goal(Conf.RIGHT)]
        self.score = Score()
        self.sys_info = SysInfo(self)
        self.controller = Controllers(self.robot)

        # Set up some variables for neural net step function
        if self.robot.side == Conf.LEFT:
            self.ball_bounce_x = Conf.FIELD_RIGHT - self.ball.rect.width
        else:
            self.ball_bounce_x = Conf.ORIGIN[X] + self.ball.rect.width

        self.rest_positions()
        # Create clock for consistent loop intervals
        self.clock = pygame.time.Clock()

    def start_man_calc(self):  # manual and calculated
        self._init()
        while ExitCtr.gen:
            # Control robot
            self.controller.manual_control()
            if DoFlag.auto_calc:
                self.controller.calculated_control()

            # Update game state
            Sprites.every.update()
            Frames.update()

            if DoFlag.update_frame:
                # Control loop intervals
                self.clock.tick(Conf.FPS)  # Comment out to remove fps limit

                # Update drawing if required
                Gen.screen.fill(Conf.WHITE)  # Reset screen for fresh drawings

                # Draw field borders
                pygame.draw.rect(Gen.screen, Conf.BLACK, self.rect, 1)

                # Draw everything and update the display
                Sprites.every.draw(Gen.screen)
                pygame.display.update()

        self.exit()

    def frame_step(self, action):
        """
        param:
        action --> tuple(
            direction --> 0 (left), 1 (right)
            angle --> 1 - 12 (0 to 180/angle_increment )
            distance --> 0 to 60 (0 to 300/move_dist)
            kick --> 0 (don't kick) or 1 (kick)
            continue --> 0 (don't continue) or 1 (continue)
        )

        return:
        x --> 0 to 600 (x coordinate)
        y --> 0 to 400 (y coordinate)

        # Ball relative conditions
        ball_flag --> 0 (not seen) or 1 (seen)
        ball_theta --> 0 to 360/angle_increment
        ball_dist --> 0 to 600/move_dist

        # Own goal relative conditions
        own_goal_theta --> 0 to 360/angle_increment
        own_goal_dist --> 0 to 600/move_dist

        # Opponent goal conditions
        opp_goal_theta --> 0 to 360/angle_increment
        opp_goal_dist --> 0 to 600/move_dist

        # Kick results given 0 or 1 for only one frame
        is_kick_success --> 0 (null) or 2 (miss) or 1 (hit)
        is_kick_accurate --> 0 (null) or 2 (bad miss) or 1 (near miss)

        # State flags
        is_kicking --> 0 (not kicking) or 1 (is kicking)
        is_moving --> 0 (not moving) or 1 (is moving)
        is_ball_moved -- > 0 (not moved recently) or 1 (moved recently)
        is_goal_scored --> 2 (own goal scored) 0 (not scored) or 1 (scored)

        time --> time since start (calculated based on frames)
        """
        # Attempt to instantiate which will only be done if not done already
        self._init()

        NULL = 0
        STATE1 = 1
        STATE2 = 2

        # Reset goal to not scored
        self._goal_scored(reset=True)

        # Get action commands
        direction, theta, dist, kick, cont = action
        theta *= Conf.DIR_OFFSET
        dist *= Conf.MOVE_DIST
        if direction == 1:
            direction = Conf.RIGHT
        elif direction == 0:
            direction = Conf.LEFT
        else:
            raise ValueError(
                f"{direction} is not a valid option. Must be 0 or 1"
            )

        # Create return away
        ret_val = np.zeros(fsr.NUM_VAL)
        ret_val[fsr.ACT_DIR] = action[0]
        ret_val[fsr.ACT_THETA] = action[1]
        ret_val[fsr.ACT_DIST] = action[2]
        ret_val[fsr.ACT_KICK] = action[3]
        ret_val[fsr.ACT_CONT] = action[4]

        # Get vector positions (relative positions)
        to_ball_s, _, _ = self.controller.get_vec()
        ball_dist, ball_theta = to_ball_s.as_polar()

        if not cont:
            # Validate data
            if ret_val[fsr.ACT_THETA] > 360/Conf.DIR_OFFSET:
                print(
                    f"Warning {ret_val[fsr.ACT_THETA]} out of range "
                    f"{360/Conf.DIR_OFFSET}"
                )
            if ret_val[fsr.ACT_DIST] > Conf.WIDTH/Conf.MOVE_DIST:
                print(
                    f"Warning {ret_val[fsr.ACT_DIST]} out of range "
                    f"{Conf.WIDTH/Conf.MOVE_DIST}"
                )
            self.net[Conf.DIRECTION] = direction
            self.net[Conf.THETA] = theta * Conf.DIR_OFFSET
            self.net[Conf.DIST] = dist * Conf.MOVE_DIST
            self.net[Conf.KICK] = kick

        # In case no kick was performed set to null value
        ret_val[fsr.IS_KICK_ACCURATE] = ret_val[fsr.IS_KICK_SUCCESS] = NULL
        if Frames.time() - Gen.last_kick_time < Conf.KICK_COOLDOWN:
            ret_val[fsr.IS_KICKING] = 1
        elif self.net[Conf.KICK] == 1:
            is_kicked = self.robot.kick()
            self.net[Conf.KICK] = False
            Gen.last_kick_time = Frames.time()

            # If within kick range
            if is_kicked:
                ret_val[fsr.IS_KICK_SUCCESS] = STATE1
            else:
                ret_val[fsr.IS_KICK_SUCCESS] = STATE2

        elif self.net[Conf.THETA] > 0:
            self.robot.move(self.net[Conf.DIRECTION])
            self.net[Conf.THETA] -= Conf.DIR_OFFSET
        elif self.net[Conf.DIST] > 0:
            self.robot.move(Conf.FORWARD)
            self.net[Conf.DIST] -= Conf.MOVE_DIST

        # Update game state
        Sprites.every.update()
        Frames.update()

        # Update drawing if required
        if DoFlag.update_frame:
            self.clock.tick(Conf.FPS)  # Regulate FPS if desired
            Gen.screen.fill(Conf.WHITE)  # Reset screen for fresh drawings

            # Draw field borders
            pygame.draw.rect(Gen.screen, Conf.BLACK, self.rect, 1)

            # Draw everything and update the display
            Sprites.every.draw(Gen.screen)
            pygame.display.update()

        # Update return Values
        to_ball, to_goal, to_own_goal = self.controller.get_vec()
        ret_val[fsr.BALL_DIST], ret_val[fsr.BALL_THETA] = to_ball.as_polar()
        ret_val[fsr.OPP_GOAL_DIST], ret_val[fsr.OPP_GOAL_THETA] = (
            to_goal.as_polar()
        )
        ret_val[fsr.OWN_GOAL_DIST], ret_val[fsr.OWN_GOAL_THETA] = (
            to_own_goal.as_polar()
        )
        if self.robot.move_angle < -90 and ball_theta > 90:  # Edge case
            if self.robot.move_angle + 360 - ball_theta <= Conf.HALF_VIS_THETA:
                ret_val[fsr.BALL_FLAG] = STATE1
        elif self.robot.move_angle > 90 and ball_theta < -90:  # Edge case
            if ball_theta + 360 - self.robot.move_angle <= Conf.HALF_VIS_THETA:
                ret_val[fsr.BALL_FLAG] = STATE1
        elif abs(self.robot.move_angle - ball_theta) <= Conf.HALF_VIS_THETA:
            # If within field of view
            ret_val[fsr.BALL_FLAG] = STATE1

        # If ball_start_pos != current_ball_pos then ball moving
        if to_ball != to_ball_s:
            ret_val[fsr.IS_BALL_MOVED] = STATE1

        # If still has angle change or distance change then moving
        if self.net[Conf.THETA] > 0 or self.net[Conf.DIST] > 0:
            ret_val[fsr.IS_MOVING] = STATE1

        # Check if goal scored this frame
        if self.is_goal_scored:
            if (  # If close to opponent goal then scored and accurate
                    self.ball.side == self.robot.side
            ):
                ret_val[fsr.IS_GOAL_SCORED] = STATE1
                ret_val[fsr.IS_KICK_ACCURATE] = STATE1
            else:  # If not close to target then own goal
                ret_val[fsr.IS_GOAL_SCORED] = STATE2
                ret_val[fsr.IS_KICK_ACCURATE] = NULL
        elif (  # if ball in wall bounce x location  check next condition
                # If ball is within range of y value
                self.controller.goal_cen.y
                - 1 * self.controller.goal.rect.height
                < self.balls[0].rect.centery <
                self.controller.goal_cen.y
                + 1 * self.controller.goal.rect.height
        ):
            if (  # If hit the wall close to the goal
                    self.ball.rect.centerx > self.ball_bounce_x
                    and self.robot.side == Conf.LEFT
            ):
                if not self.is_accurate_sent:
                    ret_val[fsr.IS_KICK_ACCURATE] = STATE1
                    self.is_accurate_sent = True
            elif (
                    self.ball.rect.centerx < self.ball_bounce_x
                    and self.robot.side == Conf.RIGHT
            ):
                if not self.is_accurate_sent:
                    ret_val[fsr.IS_KICK_ACCURATE] = STATE1
                    self.is_accurate_sent = True
            else:  # If not against respective wall accuracy was not sent
                self.is_accurate_sent = False
        else:
            if (
                    self.ball.rect.centerx > self.ball_bounce_x
                    and self.robot.side == Conf.LEFT
            ):
                if not self.is_accurate_sent:
                    ret_val[fsr.IS_KICK_ACCURATE] = STATE2
                    self.is_accurate_sent = True
            elif (
                    self.ball.rect.centerx < self.ball_bounce_x
                    and self.robot.side == Conf.RIGHT
            ):
                if not self.is_accurate_sent:
                    ret_val[fsr.IS_KICK_ACCURATE] = STATE2
                    self.is_accurate_sent = True
            else:
                self.is_accurate_sent = False

        ret_val[fsr.X] = self.robot.rect.centerx
        ret_val[fsr.Y] = self.robot.rect.centery
        ret_val[fsr.TIME] = Frames.time()
        return ret_val

    def score_goal(self, score_time, score_side):
        self._goal_scored()
        self.score.update_score(score_side)
        record = (
            self.start_robot,
            self.start_ball,
            score_time,
            score_side,
            self.algorithm
        )
        self.game_records.append(record)
        self.rest_positions()

    def rest_positions(self):
        self.num_reset += 1
        for robot in Sprites.robots:
            if self.num_reset < len(self.robot_xy):
                robot.rect.centerx, robot.rect.centery = (
                    self.robot_xy[self.num_reset]
                )
            else:  # get random pos
                # Random y position within offset
                robot.rect.centery = random.randint(
                    self.pos_offset + Conf.ORIGIN[Y],
                    Conf.FIELD_BOT - self.pos_offset
                )
                # Random x pos based on side
                if robot.side == Conf.LEFT:
                    robot.rect.centerx = random.randint(
                        self.pos_offset + Conf.ORIGIN[X], Conf.CENTER[X]
                    )
                    robot.direction_angle = 0
                    robot.place_dir_arrow()
                else:
                    robot.rect.centerx = random.randint(
                        Conf.CENTER[X], Conf.FIELD_RIGHT - self.pos_offset
                    )
                    robot.direction_angle = 180
                    robot.place_dir_arrow()
            # Ensure robots always start facing same direction
            if robot.side == Conf.LEFT:
                robot.direction_angle = 0
                robot.place_dir_arrow()
            else:
                robot.direction_angle = 180
                robot.place_dir_arrow()
            robot.check_bounds()

        for ball in Sprites.balls:
            if self.num_reset < len(self.ball_xy):
                # For each goal set the xy position
                ball.rect.centerx, ball.rect.centery = (
                    self.ball_xy[self.num_reset]
                )
            else:
                # Get random position
                ball.rect.centerx = random.randint(
                    self.pos_offset + Conf.ORIGIN[X],
                    Conf.FIELD_RIGHT - self.pos_offset
                )
                ball.rect.centery = random.randint(
                    self.pos_offset + Conf.ORIGIN[Y],
                    Conf.FIELD_BOT - self.pos_offset
                )
            ball.move_dist = 0
        self.start_robot = (self.robot.rect.centerx, self.robot.rect.centery)
        self.start_ball = (
            self.balls[0].rect.centerx, self.balls[0].rect.centery
        )

    def _goal_scored(self, reset=False):
        if reset:
            self.is_goal_scored = False
        else:
            self.is_goal_scored = True

    def load(self, algorithm=GS.TYPE_MAN):
        if algorithm == GS.TYPE_NONE:
            print("NOTHING DONE")
            return
        if self.algorithm == algorithm:
            print(
                "WARNING YOU ARE LOADING THE SAME TYPE OF ALGORITHM AS TO THE"
                " ONE YOU WILL BE SAVING"
            )
        for root, dirs, files in os.walk(Conf.CSV_FOLDER):
            for file in files:
                if f"good_{algorithm}" in file:
                    # index_loc = re.search(r"\d+.", file).span()
                    with open(f"{Conf.CSV_FOLDER}/{file}") as f:
                        data = list(csv.reader(f))
                    robot_xy = data[0].index(GS.ROBOT_START)
                    ball_xy = data[0].index(GS.BALL_START)
                    time_to_score = data[0].index(GS.TIME_TO_SCORE)
                    for record in data[1:]:
                        self.robot_xy.append(
                            ast.literal_eval(record[robot_xy])
                        )
                        self.ball_xy.append(ast.literal_eval(record[ball_xy]))
                        self.recorded_times.append(
                            ast.literal_eval(record[time_to_score])
                        )
        num_records = len(self.robot_xy)
        rec_per_proc = num_records // Conf.NUM_PROC
        if self.index >= 0:
            if self.index == 0:
                self.robot_xy = self.robot_xy[:rec_per_proc]
                self.ball_xy = self.ball_xy[:rec_per_proc]
                self.recorded_times = self.recorded_times[:rec_per_proc]
            elif self.index+1 == Conf.NUM_PROC:
                i = self.index
                self.robot_xy = self.robot_xy[rec_per_proc*i:]
                self.ball_xy = self.ball_xy[rec_per_proc*i:]
                self.recorded_times = self.recorded_times[rec_per_proc*i:]
            else:
                i = self.index
                j = self.index + 1
                self.robot_xy = self.robot_xy[rec_per_proc*i:rec_per_proc*j]
                self.ball_xy = self.ball_xy[rec_per_proc*i:rec_per_proc*j]
                self.recorded_times = self.recorded_times[
                                        rec_per_proc*i:rec_per_proc*j
                                      ]

    def save(self):
        if self.algorithm == GS.TYPE_NONE:
            print("No data type so not saving")
        delete_index = []
        bad_data = [self.game_records[0]]
        side_index = bad_data[0].index(GS.SIDE_SCORE)
        index = 0
        for record in self.game_records[1:]:
            index += 1
            if record[side_index] != self.robot.side:
                delete_index.append(index)
        delete_index.reverse()
        for index in delete_index:
            bad_data.append(self.game_records.pop(index))

        good_data = self.game_records
        if not os.path.isdir(Conf.CSV_FOLDER):
            os.mkdir(Conf.CSV_FOLDER)
        elif os.path.isfile(self.good_data_file):
            if len(good_data) > 1:
                good_data = self.game_records[1:]
            else:
                good_data = []
        if os.path.isfile(self.bad_data_file):
            bad_data.pop()

        with open(self.good_data_file, 'a') as file:
            writer = csv.writer(file)
            writer.writerows(good_data)
        with open(self.bad_data_file, 'a') as file:
            writer = csv.writer(file)
            writer.writerows(bad_data)

    def exit(self):
        if DoFlag.save_data:
            self.save()
        pygame.quit()

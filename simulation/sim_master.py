import csv
import os
import random

import pygame

from config import Conf, GS
from controls import Controllers
from variables import Gen, ExitCtr, Frames, Sprites, DoFlag
from sim_objects import Robot, Ball, Goal, Score, SysInfo
X = Conf.X
Y = Conf.Y


class SimMaster:
    def __init__(self, index):
        self.index = index

        self.robots = []
        self.balls = []
        self.goals = []

        self.controller = None
        self.clock = None
        self.score = None
        self.sys_info = None

        self.robot_xy = []
        self.ball_xy = []
        self.pos_offset = Conf.RBT_SIZE[0]

        # Record information for later benchmarking neural net against "math"
        self.game_records = [
            (
                GS.ROBOT_START, GS.BALL_START,
                GS.TIME_TO_SCORE, GS.SIDE_SCORE, GS.METHOD
            )
        ]

        if len(self.robot_xy) != len(self.ball_xy):
            raise IndexError("None matching data set for ball and robot pos")

    def start(self):
        pygame.init()
        # Set up simulation window
        height = Conf.HEIGHT + Conf.PADDING
        width = Conf.WIDTH + Conf.PADDING
        Gen.screen = pygame.display.set_mode((width, height))
        Gen.screen.fill(Conf.WHITE)

        # Field border rectangle dimensions
        rect = (Conf.ORIGIN[X], Conf.ORIGIN[Y], Conf.WIDTH, Conf.HEIGHT)

        # Create all simulation objects
        self.robots = [Robot(side=Conf.LEFT)]
        self.balls = [Ball(master=self)]
        self.goals = [Goal(Conf.LEFT), Goal(Conf.RIGHT)]
        self.score = Score()
        self.sys_info = SysInfo(self)
        self.controller = Controllers(self.robots[0])

        # Create clock for consistent loop intervals
        self.clock = pygame.time.Clock()
        while ExitCtr.gen:
            # Control loop intervals
            self.clock.tick(Conf.FPS)
            Gen.screen.fill(Conf.WHITE)  # Reset screen for fresh drawings

            # Draw field borders
            pygame.draw.rect(Gen.screen, (9, 9, 9), rect, 1)

            # Control robot
            self.controller.manual_control()
            if DoFlag.auto_calc:
                self.controller.calculated_control()

            # Update game state
            Sprites.every.update()
            Sprites.every.draw(Gen.screen)
            pygame.display.update()
            Frames.update()

        self.save()
        pygame.quit()

    def score_goal(self, score_time, score_side):
        self.score.update_score(score_side)
        record = (
            (self.robots[0].rect.centerx, self.robots[0].rect.centery),
            (self.balls[0].rect.centerx, self.balls[0].rect.centery),
            score_time,
            score_side,
            GS.TYPE_ALG
        )
        self.game_records.append(record)
        self.rest_positions()

    def rest_positions(self):
        # Get total score to know how many goals have been completed
        for robot in Sprites.robots:
            if self.score.total < len(self.robot_xy):
                # For each goal set the xy position
                robot.rect.centerx, robot.rect.centery = (
                    self.robot_xy[self.score.total]
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
                robot.check_bounds()

        for ball in Sprites.balls:
            if self.score.total < len(self.ball_xy):
                # For each goal set the xy position
                ball.rect.centerx, ball.rect.centery = (
                    self.ball_xy[self.score.total]
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

    def save(self):
        delete_index = []
        bad_data = [self.game_records[0]]
        index = 0
        for record in self.game_records[1:]:
            index += 1
            if record[-1] != self.robots[0].side:
                delete_index.append(index)
        delete_index.reverse()
        for index in delete_index:
            bad_data.append(self.game_records.pop(index))

        good_data = self.game_records
        good = f"{Conf.CSV}/good.csv"
        bad = f"{Conf.CSV}/bad.csv"
        if not os.path.isdir(Conf.CSV):
            os.mkdir(Conf.CSV)
        elif os.path.isfile(good):
            if len(good_data) > 1:
                good_data = self.game_records[1:]
            else:
                good_data = []
        if os.path.isfile(bad):
            bad_data.pop()

        with open(good, 'a') as file:
            writer = csv.writer(file)
            writer.writerows(good_data)
        with open(bad, 'a') as file:
            writer = csv.writer(file)
            writer.writerows(bad_data)

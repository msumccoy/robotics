"""
This file is used to control the robot via keyboard control
"""
import os
import sys
import csv
import pygame
import time
from pygame.math import Vector2

from config import Conf, GS
from variables import DoFlag, Gen, Sprites, ExitCtr


class Controllers:
    def __init__(self, robot):
        self.robot = robot
        self.ball = Sprites.balls.sprites()[0]
        self.side = robot.side

        self.robot_start_pos = robot.rect.centerx, robot.rect.centery
        self.ball_start_pos = self.ball.rect.centerx, self.ball.rect.centery

        self.vec_robot = Vector2()
        self.vec_ball = Vector2()
        self.waypoint_ball = Vector2()
        self.waypoint = Vector2()
        self.goal_top = Vector2()
        self.goal_bot = Vector2()
        self.goal_cen = Vector2()

        for goal in Sprites.goals:
            if goal.side == self.side:
                self.own_goal = goal
            else:
                self.goal = goal

        self.goal_top.y = self.goal.rect.y
        self.goal_cen.y = self.goal.rect.centery
        self.goal_bot.y = self.goal.rect.y + self.goal.rect.height
        if self.goal.side == Conf.RIGHT:
            self.goal_top.x = self.goal_bot.x = self.goal_cen.x \
                = self.goal.rect.x
        else:
            self.goal_top.x = self.goal_bot.x = self.goal_cen.x \
                = self.goal.rect.x + self.goal.rect.width

        self.to_waypoint = True
        self.to_ball = True
        self.is_new_waypoint = True
        self.adjust_ball = False

        self.game_state = [  # NAME TO BE CHANGED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            (GS.ROBOT_START,  GS.BALL_START, GS.TIME_TO_SCORE, GS.SIDE_SCORE)
        ]

    def check_score(self):
        if self.ball.score_side is not None:

            record = (
                self.robot_start_pos,
                self.ball_start_pos,
                self.ball.score_time,
                self.ball.score_side
            )
            self.game_state.append(record)
            self.ball.reset_record()
            self.robot_start_pos = (
                self.robot.rect.centerx, self.robot.rect.centery
            )
            self.ball_start_pos = (
                self.ball.rect.centerx, self.ball.rect.centery
            )

    def calculated_control(self):
        # Update robot and ball position
        self.vec_robot.x = self.robot.rect.centerx
        self.vec_robot.y = self.robot.rect.centery
        self.vec_ball.x = self.ball.rect.centerx
        self.vec_ball.y = self.ball.rect.centery

        if self.side == Conf.LEFT:
            if self.to_waypoint:
                if self.is_new_waypoint:
                    self.is_new_waypoint = False

                    # Save the position of where the ball should be
                    self.waypoint_ball.x = self.vec_ball.x
                    self.waypoint_ball.y = self.vec_ball.y

                    # Set way point
                    offset = self.goal_cen - self.vec_ball
                    if self.goal_cen == self.vec_ball:
                        offset.x = Conf.WIDTH
                        offset.y = Conf.HEIGHT
                    offset.scale_to_length(-50)
                    self.waypoint = self.vec_ball + offset
                    if self.robot.half_len > self.waypoint.x:
                        self.waypoint.x = self.vec_ball.x - offset.x
                    elif Conf.WIDTH - self.robot.half_len < self.waypoint.x:
                        self.waypoint.x = self.vec_ball.x - self.robot.half_len
                    if not(
                            self.robot.half_len
                            < self.waypoint.y
                            < Conf.HEIGHT - self.robot.half_len
                    ):
                        self.waypoint.y = self.vec_ball.y - offset.y

                if self.waypoint_ball == self.vec_ball:
                    to_waypoint = self.waypoint - self.vec_robot
                    dist, angle = to_waypoint.as_polar()
                    angle_dif = angle - self.robot.move_angle
                    if angle_dif < -Conf.DIR_OFFSET:
                        self.robot.move(Conf.LEFT)
                    elif angle_dif > Conf.DIR_OFFSET:
                        self.robot.move(Conf.RIGHT)
                    else:
                        if dist < 5:
                            self.to_waypoint = False
                            self.to_ball = True
                        else:
                            self.robot.move(Conf.FORWARD)
                else:
                    self.is_new_waypoint = True
            elif self.to_ball:
                if self.waypoint_ball == self.vec_ball:
                    to_ball = self.vec_ball - self.vec_robot
                    dist, angle = to_ball.as_polar()
                    if angle + Conf.DIR_OFFSET - 1 < self.robot.move_angle:
                        self.robot.move(Conf.LEFT)
                    elif angle - Conf.DIR_OFFSET + 1 > self.robot.move_angle:
                        self.robot.move(Conf.RIGHT)
                    else:
                        self.robot.kick()
                        self.robot.move(Conf.FORWARD)
                else:
                    self.is_new_waypoint = True
                    self.to_waypoint = True
                    self.to_ball = False

            if DoFlag.show_vectors:
                pygame.draw.line(
                    Gen.screen, (255, 0, 0), self.vec_ball, self.goal_top
                )
                pygame.draw.line(
                    Gen.screen, (255, 0, 0), self.vec_ball, self.goal_bot
                )
                pygame.draw.line(
                    Gen.screen, (255, 0, 0), self.vec_ball, self.goal_cen
                )
                pygame.draw.line(
                    Gen.screen, (255, 0, 0), self.vec_ball, self.waypoint
                )
                pygame.draw.line(
                    Gen.screen, (0, 0, 0), self.waypoint, self.vec_robot, 3
                )

    def manual_control(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.robot.move(Conf.UP)
        if keys[pygame.K_DOWN]:
            self.robot.move(Conf.DOWN)
        if keys[pygame.K_RIGHT]:
            self.robot.move(Conf.RIGHT)
        if keys[pygame.K_LEFT]:
            self.robot.move(Conf.LEFT)
        if keys[pygame.K_a]:
            if time.time() - Gen.key_a_time > 5 * Conf.COOLDOWN_TIME:
                Gen.key_a_time = time.time()
                DoFlag.auto_calc = not DoFlag.auto_calc
        if keys[pygame.K_b]:
            if time.time() - Gen.key_b_time > 5 * Conf.COOLDOWN_TIME:
                Gen.key_b_time = time.time()
                DoFlag.show_vectors = not DoFlag.show_vectors
        if keys[pygame.K_c]:
            if time.time() - Gen.key_b_time > 5 * Conf.COOLDOWN_TIME:
                Gen.key_c_time = time.time()
                DoFlag.show_directions = not DoFlag.show_directions
        ######################################################################
        # To delete
        dist = 5
        if keys[pygame.K_2] or keys[pygame.K_KP8]:
            # Move up
            self.ball.move(-90, dist)
        if keys[pygame.K_3] or keys[pygame.K_KP5]:
            # Move down
            self.ball.move(90, dist)
        if keys[pygame.K_1] or keys[pygame.K_KP4]:
            # Move left
            self.ball.move(180, dist)
        if keys[pygame.K_4] or keys[pygame.K_KP6]:
            # Move right
            self.ball.move(0, dist)
        ######################################################################
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ExitCtr.gen = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ExitCtr.gen = False
                elif event.key == pygame.K_SPACE:
                    self.robot.kick()

    def save(self):
        delete_index = []
        bad_data = [self.game_state[0]]
        index = 0
        for record in self.game_state[1:]:
            index += 1
            if record[-1] != self.side:
                delete_index.append(index)
        delete_index.reverse()
        for index in delete_index:
            bad_data.append(self.game_state.pop(index))

        good_data = self.game_state
        good = f"{Conf.CSV}/good.csv"
        bad = f"{Conf.CSV}/bad.csv"
        if not os.path.isdir(Conf.CSV):
            os.mkdir(Conf.CSV)
        elif os.path.isfile(good):
            if len(good_data) > 1:
                good_data = self.game_state[1:]
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

    # TODO: Enable multiple robot.
    #  - save robot controls in json file
    #  - if new robot with no controls is present create controls and save them
    #  - allow changing of controls
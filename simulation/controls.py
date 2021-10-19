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
from variables import DoFlag, Gen, Sprites, ExitCtr, Frames
X = Conf.X
Y = Conf.Y


class Controllers:
    def __init__(self, robot):
        self.robot = robot
        # Only get the first ball as we can't chase more than one
        self.ball = Sprites.balls.sprites()[0]
        self.side = robot.side

        # Save starting location for later testing
        self.robot_start_pos = robot.rect.centerx, robot.rect.centery
        self.ball_start_pos = self.ball.rect.centerx, self.ball.rect.centery

        # Vectors used for calculations
        self.vec_robot = Vector2()
        self.vec_ball = Vector2()
        self.waypoint_ball = Vector2()
        self.waypoint = Vector2()
        self.goal_top = Vector2()
        self.goal_bot = Vector2()
        self.goal_cen = Vector2()

        # Save instance of goals
        for goal in Sprites.goals:
            if goal.side == self.side:
                self.own_goal = goal
            else:
                self.goal = goal

        # Save vector location of goal
        self.goal_top.y = self.goal.rect.y
        self.goal_cen.y = self.goal.rect.centery
        self.goal_bot.y = self.goal.rect.y + self.goal.rect.height
        if self.goal.side == Conf.RIGHT:
            self.goal_top.x = self.goal_bot.x = self.goal_cen.x \
                = self.goal.rect.x
        else:
            self.goal_top.x = self.goal_bot.x = self.goal_cen.x \
                = self.goal.rect.x + self.goal.rect.width

        # Flags
        self.to_waypoint = True
        self.to_ball = True
        self.is_new_waypoint = True
        self.adjust_ball = False

    def calculated_control(self):
        # Update robot and ball vector position
        self.vec_robot.x = self.robot.rect.centerx
        self.vec_robot.y = self.robot.rect.centery
        self.vec_ball.x = self.ball.rect.centerx
        self.vec_ball.y = self.ball.rect.centery

        if self.side == Conf.LEFT:  # Must later be done for the right side
            if self.to_waypoint:  # Go to way point if has not reached yet
                if self.is_new_waypoint:  # Set new way point if ball has moved
                    self.is_new_waypoint = False

                    # Save the position of where the ball should be
                    self.waypoint_ball.x = self.vec_ball.x
                    self.waypoint_ball.y = self.vec_ball.y

                    # Set way point
                    offset = self.goal_cen - self.vec_ball
                    if self.goal_cen == self.vec_ball:
                        # Offest does not matter just can't be 0 when ball
                        # which happens when ball hits the center
                        offset.x = Conf.WIDTH
                        offset.y = Conf.HEIGHT
                    offset.scale_to_length(-50)
                    self.waypoint = self.vec_ball + offset
                    # If way point is too close to the left wall
                    if self.robot.half_len > self.waypoint.x - Conf.ORIGIN[X]:
                        if (  # If ball is close to own goal
                                self.goal_top.y - 50
                                < self.waypoint.y
                                < self.goal_bot.y + 50
                        ):
                            self.waypoint.y = self.vec_ball.y + 50
                            self.waypoint.x = (
                                    self.robot.half_len + 1 + Conf.ORIGIN[X]
                            )
                        else:
                            self.waypoint.x = self.vec_ball.x - offset.x
                    elif (  # If way point is too close to the right wall
                            Conf.FIELD_RIGHT - self.robot.half_len
                            < self.waypoint.x
                    ):
                        self.waypoint.x = (
                                self.vec_ball.x - self.robot.half_len - 1
                        )
                    if not(  # If way point too close to top or bottom
                            self.robot.half_len + Conf.ORIGIN[Y]
                            < self.waypoint.y
                            < Conf.FIELD_BOT - self.robot.half_len
                    ):
                        self.waypoint.y = self.vec_ball.y - offset.y

                # If ball has not moved
                if self.waypoint_ball == self.vec_ball:
                    to_waypoint = self.waypoint - self.vec_robot
                    dist, angle = to_waypoint.as_polar()
                    angle_dif = angle - self.robot.move_angle
                    # If the angle difference is not within range change angle
                    if angle_dif < -Conf.DIR_OFFSET:
                        self.robot.move(Conf.LEFT)
                    elif angle_dif > Conf.DIR_OFFSET:
                        self.robot.move(Conf.RIGHT)
                    else:
                        # If angle within range but not close to waypoint move
                        # towards waypoint
                        if dist < 5:
                            # If at way poin set to go to ball
                            self.to_waypoint = False
                            self.to_ball = True
                        else:
                            self.robot.move(Conf.FORWARD)
                else:
                    self.is_new_waypoint = True
            elif self.to_ball:
                # If ball has not moved
                if self.waypoint_ball == self.vec_ball:
                    to_ball = self.vec_ball - self.vec_robot
                    dist, angle = to_ball.as_polar()
                    # If angle not within range change angle
                    if angle + Conf.DIR_OFFSET - 1 < self.robot.move_angle:
                        self.robot.move(Conf.LEFT)
                    elif angle - Conf.DIR_OFFSET + 1 > self.robot.move_angle:
                        self.robot.move(Conf.RIGHT)
                    else:
                        # if angle within range try to kick the ball then move
                        self.robot.kick()
                        self.robot.move(Conf.FORWARD)
                else:
                    self.is_new_waypoint = True
                    self.to_waypoint = True
                    self.to_ball = False

            if DoFlag.show_vectors:  # Draw vector lines if desired
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
        # User toggle based on real world time
        if keys[pygame.K_a]:
            if time.time() - Gen.key_a_time > 10 * Conf.COOLDOWN_TIME:
                Gen.key_a_time = time.time()
                DoFlag.auto_calc = not DoFlag.auto_calc
        if keys[pygame.K_b]:
            if time.time() - Gen.key_b_time > 10 * Conf.COOLDOWN_TIME:
                Gen.key_b_time = time.time()
                DoFlag.show_vectors = not DoFlag.show_vectors
        if keys[pygame.K_c]:
            if time.time() - Gen.key_b_time > 10 * Conf.COOLDOWN_TIME:
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

    # TODO: Enable multiple robot.
    #  - save robot controls in json file
    #  - if new robot with no controls is present create controls and save them
    #  - allow changing of controls

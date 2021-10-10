"""
This file is used to control the robot via keyboard control
"""
import sys
import pygame
import time
from pygame.math import Vector2

from config import Conf
from classes import all_sprites, robot_sprites, ball_sprites, goal_sprites
from variables import DoFlag, Gen


class Controllers:
    def __init__(self, robot, t):
        self.t = t
        self.robot = robot
        self.side = robot.side
        self.vec_ball = Vector2()
        self.vec_goal = Vector2()
        self.vec = Vector2()
        for goal in goal_sprites:
            if goal.side == self.side:
                self.own_goal = goal
            else:
                self.goal = goal

        self.ball = ball_sprites.sprites()[0]

    def calculated_control(self):
        if self.side == Conf.LEFT:
            self.vec_ball.x = self.ball.rect.x
            self.vec_ball.y = self.ball.rect.centery
            self.vec_goal.x = self.goal.rect.x
            self.vec_goal.y = self.goal.rect.centery
            self.vec.x = self.robot.rect.centerx
            self.vec.y = self.robot.rect.centery

        # self.vec_ball, self.vec_goal
        self.vec_ball_to_goal = self.vec_goal - self.vec_ball
        self.vec_to_ball = self.vec_ball - self.vec
        dist, angle = self.vec_to_ball.as_polar()
        _, target_angle = self.vec_ball_to_goal.as_polar()
        if (
                dist < self.robot.half_len + Conf.HALF_RANGE -1
                and
                target_angle - Conf.DIRECTION_OFFSET
                < angle
                < target_angle + Conf.DIRECTION_OFFSET
        ):
            if self.robot.move_angle != angle:
                self.robot.move(Conf.RIGHT)
            self.robot.kick()
        else:
            if int(self.robot.move_angle) != int(angle):
                if self.robot.move_angle - angle < 0:
                    self.robot.move(Conf.RIGHT)
                else:
                    self.robot.move(Conf.LEFT)
                print(f"angle sent {angle}")
                angle = self.robot.limit_angle(angle=angle)
                print(f"{int(self.robot.move_angle)}--{int(angle)}")

        pygame.draw.line(self.t, (255,0,0),self.vec_ball, self.vec_goal)
        pygame.draw.line(self.t, (255,0,0),self.vec_ball, self.vec)

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
            if time.time() - Gen.key_a_pressed > .5:
                Gen.key_a_pressed = time.time()
                DoFlag.auto_calc = not DoFlag.auto_calc
        if keys[pygame.K_b]:
            if time.time() - Gen.key_a_pressed > .5:
                Gen.key_a_pressed = time.time()
                DoFlag.chan = not DoFlag.chan
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    self.robot.kick()

    # TODO: Enable multiple robot.
    #  - save robot controls in json file
    #  - if new robot with no controls is present create controls and save them
    #  - allow changing of controls
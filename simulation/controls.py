"""
This file is used to control the robot via keyboard control
"""
import sys
import pygame
import time
from pygame.math import Vector2

from config import Conf
from variables import DoFlag, Gen, Sprites


class Controllers:
    def __init__(self, robot):
        self.robot = robot
        self.side = robot.side

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

        self.to_way_point = False

        self.ball = Sprites.balls.sprites()[0]

    def calculated_control(self):
        # Update robot and ball position
        self.vec_robot.x = self.robot.rect.centerx
        self.vec_robot.y = self.robot.rect.centery
        self.vec_ball.x = self.ball.rect.centerx
        self.vec_ball.y = self.ball.rect.centery

        if self.side == Conf.LEFT:
            vec_to_ball = self.vec_ball - self.vec_robot
            vec_ball_to_goal_top = self.goal_top - self.vec_ball
            vec_ball_to_goal_bot = self.goal_bot - self.vec_ball
            dist, to_ball = vec_to_ball.as_polar()
            _, ball_to_top = vec_ball_to_goal_top.as_polar()
            _, ball_to_bot = vec_ball_to_goal_bot.as_polar()

            target_dist = self.robot.half_len + Conf.HALF_RANGE

            if self.to_way_point:
                vec_ball_to_goal_cen = self.goal_cen - self.vec_ball
                vec_ball_to_goal_cen.scale_to_length(100)
                self.vec_ball.x = self.vec_ball.x - vec_ball_to_goal_cen.x
                self.vec_ball.y = self.vec_ball.y - vec_ball_to_goal_cen.y
                # print(vec_ball_to_goal_cen)
            elif dist < target_dist or self.vec_robot.x > self.vec_ball.x:
                if self.robot.in_range(dist) and self.vec_robot.x < self.vec_ball.x:
                    print(f"{self.vec_robot}, {self.vec_ball}")
                    angle = self.robot.limit_angle(self.robot.move_angle)
                    if angle <= to_ball - Conf.DIRECTION_OFFSET:
                        print(angle, to_ball - Conf.DIRECTION_OFFSET)
                        print(f"MOVE right {self.vec_robot}!!!!!!!!!!!!!!!!!!!!!!!")
                        self.robot.move(Conf.RIGHT)
                    elif angle >= to_ball + Conf.DIRECTION_OFFSET:
                        print(f"MOVE left {self.vec_robot}!!!!!!!!!!!!!!!!!!!!!!!!")
                        self.robot.move(Conf.LEFT)
                    elif self.vec_robot.x < self.vec_ball.x - x_offset:
                        print(f"KICK {self.vec_robot}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        self.robot.kick()
                    else:
                        self.to_way_point = True
                        print("self.robot.move(Conf.DOWN)")
                else:
                    if self.vec_ball.y < self.goal_top.y:
                        y_offset = -50
                    elif self.vec_ball.y > self.goal_bot.y:
                        y_offset = 50
                    else:
                        y_offset = 0

                    self.vec_ball.y -= y_offset
                    self.vec_ball.x -= x_offset

                    vec_to_ball = self.vec_ball - self.vec_robot
                    dist, to_ball = vec_to_ball.as_polar()
                    max_angle = to_ball + Conf.DIRECTION_OFFSET + 1
                    min_angle = to_ball - Conf.DIRECTION_OFFSET - 1
                    if min_angle > self.robot.move_angle:
                        self.robot.move(Conf.RIGHT)
                    elif max_angle < self.robot.move_angle:
                        print("self.robot.move(Conf.LEFT)")
                        self.robot.move(Conf.LEFT)
                    else:
                        self.robot.move(Conf.FORWARD)
                    print(self.vec_robot, self.vec_ball, dist, target_dist)
            else:
                while x_offset > dist:
                    x_offset /= 2
                if x_offset < target_dist:
                    x_offset = target_dist

                if not(ball_to_top < to_ball < ball_to_bot) and dist > x_offset:
                    self.vec_ball.x -= x_offset
                    vec_to_ball = self.vec_ball - self.vec_robot
                    dist, to_ball = vec_to_ball.as_polar()
                max_angle = to_ball + Conf.DIRECTION_OFFSET + 1
                min_angle = to_ball - Conf.DIRECTION_OFFSET - 1

                if min_angle > self.robot.move_angle:
                    self.robot.move(Conf.RIGHT)
                elif max_angle < self.robot.move_angle:
                    self.robot.move(Conf.LEFT)
                else:
                    self.robot.move(Conf.FORWARD)
                if ball_to_top < to_ball < ball_to_bot:
                    self.robot.kick()

            # in_range = self.robot.in_range(dist)
            # if ball_to_top < to_ball < ball_to_bot and in_range:
            #     angle = self.robot.move_angle
            #     if angle - Conf.DIRECTION_OFFSET + 1> angle:
            #         self.robot.move(Conf.RIGHT)
            #     elif angle + Conf.DIRECTION_OFFSET - 1 <= angle:
            #         self.robot.move(Conf.LEFT)
            #     else:
            #         self.robot.kick()
            # elif ball_to_top < to_ball < ball_to_bot:
            #
            # else:
            #     if min_angle > self.robot.move_angle:
            #         self.robot.move(Conf.RIGHT)
            #     elif max_angle < self.robot.move_angle:
            #         self.robot.move(Conf.LEFT)
            #     else:
            #         self.robot.move(Conf.FORWARD)
            if DoFlag.temp_b:
                print(f"dist {dist}, angle {to_ball}")
                print(f"angle to top {ball_to_top}")
                print(f"angle to bottom {ball_to_bot}")
                # print()
                print(f"vec_to_ball {vec_to_ball}")
                print(f"ball to top {vec_ball_to_goal_top}")
                print(f"ball to bot {vec_ball_to_goal_bot}")
                print()

        # else:
        #     self.vec_ball.x = self.ball.rect.x + self.ball.rect.width
        #     self.vec_ball.y = self.ball.rect.centery
        #     self.vec_goal.x = self.goal.rect.x
        #     self.vec_goal.y = self.goal.rect.centery
        #     self.vec.x = self.robot.rect.centerx
        #     self.vec.y = self.robot.rect.centery

        pygame.draw.line(
            Gen.screen, (255, 0, 0), self.vec_ball, self.goal_top
        )
        pygame.draw.line(
            Gen.screen, (255, 0, 0), self.vec_ball, self.goal_bot
        )
        pygame.draw.line(
            Gen.screen, (255, 0, 0), self.vec_ball, self.goal_cen
        )
        pygame.draw.line(Gen.screen, (0, 0, 0), self.vec_ball, self.vec_robot, 3)
        # pygame.draw.line(
        #     Gen.screen, (255, 0, 0),
        #     (self.ball.rect.centerx, self.ball.rect.centery),
        #     (
        #         self.ball.rect.centerx + vec_ball_to_goal_top.x,
        #         self.ball.rect.centery + vec_ball_to_goal_top.y
        #     ),
        # )

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
            if time.time() - Gen.key_b_pressed > .5:
                Gen.key_b_pressed = time.time()
                DoFlag.temp_b = not DoFlag.temp_b
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
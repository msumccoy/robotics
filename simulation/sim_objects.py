"""
This holds all coding simulation objects such as score num, robot, goal, ect.
"""
import random
import time

import pygame
from pygame.math import Vector2

from config import Conf, Physics
from variables import Score, PlayerCount, ExitCtr, DoFlag, Sprites, Gen, Frames


class BaseClass(pygame.sprite.Sprite):
    def __init__(self, size, pos=(0, 0), color=Conf.COLOR1, text="Base"):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(Conf.ALPHA_COLOR)
        self.image.set_colorkey(Conf.ALPHA_COLOR)
        self.rect = self.image.get_rect()
        ######################################################################
        # This should be replaced with an actual image later on likely  ######
        ######################################################################
        pygame.draw.circle(
            self.image, color, self.rect.center, self.rect.width//2
        )
        self.font = pygame.font.SysFont('arial', 10)
        text = self.font.render(text, True, Conf.BLACK)
        text_rect = text.get_rect()
        text_rect.center = (self.rect.width//2, self.rect.height//2)
        self.image.blit(text, text_rect)
        ######################################################################
        self.vec = Vector2()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.move_dist = 5
        self.size = size
        self.move_angle = 0
        self.half_len = size[0]//2
        Sprites.every.add(self)

    def move(self, move_dir, distance=None):
        if distance is None:
            distance = self.move_dist
        self.vec.from_polar((distance, move_dir))
        self.rect.centerx += self.vec.x
        self.rect.centery += self.vec.y
        self.check_bounds()  # Make sure did not move out of field

    def check_bounds(self):
        if self.rect.top < 0:
            # If higher than 0 on y axis
            self.rect.y = 0
        elif self.rect.bottom > Conf.HEIGHT:
            # If lower than the bottom of y axis
            self.rect.y = Conf.HEIGHT - self.rect.height
        if self.rect.left < 0:
            # If further than 0 on x axis
            self.rect.x = 0
        elif self.rect.right > Conf.WIDTH:
            # If further than max on x axis
            self.rect.x = Conf.WIDTH - self.rect.width

    def change_speed(self, direction):
        if direction == Conf.UP:
            self.move_dist += 1
        if direction == Conf.DOWN:
            self.move_dist -= 1

    def limit_angle(self, angle=None):
        # Pygame angle goes from -180 to 180
        upper = 180
        lower = -180
        self_angle = False
        if angle is None:
            angle = self.move_angle
            self_angle = True

        while angle > upper:
            angle -= 360
        while angle < lower:
            angle += 360

        if self_angle:
            self.move_angle = angle
        else:
            return angle

    def draw_movement_line(self):
        self.vec.from_polar((Conf.WIDTH, self.move_angle))
        self.vec.x += self.rect.centerx
        self.vec.y += self.rect.centery
        end = Vector2(self.vec)
        self.vec.from_polar((-Conf.WIDTH, self.move_angle))
        self.vec.x += self.rect.centerx
        self.vec.y += self.rect.centery
        start = Vector2(self.vec)
        pygame.draw.line(Gen.screen, (25, 255, 245), start, end)


class Robot(BaseClass):
    def __init__(self, size=Conf.RBT_SIZE, pos=None, img=None, side=None):
        if side == Conf.LEFT:
            color = Conf.COLOR_LEFT
            PlayerCount.left += 1
            if pos is None:
                pos = (
                    random.randint(0, Conf.WIDTH//2),
                    random.randint(0, Conf.HEIGHT)
                )
        elif side == Conf.RIGHT:
            color = Conf.COLOR_RIGHT
            PlayerCount.left += 1
            if pos is None:
                pos = (
                    random.randint(Conf.WIDTH//2, Conf.WIDTH),
                    random.randint(0, Conf.HEIGHT)
                )
            self.move_angle = 180
        else:
            raise ValueError(
                f"Error side must either be '{Conf.LEFT}' or '{Conf.RIGHT}'"
            )
        super().__init__(size, pos=pos, text="RBT", color=color)
        if img is not None:
            print(f"Apply image to self.image")
        self.image_org = self.image.copy()  # Save a copy of image for refresh

        # Create direction indicator
        arrow_size = (size[0] // 5, size[1] // 5)
        self.dir_arrow = pygame.Surface(arrow_size)
        self.dir_arrow.fill(Conf.BLACK)
        self.dir_arrow_rect = self.dir_arrow.get_rect()
        self.dir_arrow_offset = (
            self.dir_arrow_rect.width / 2,
            self.dir_arrow_rect.height / 2
        )

        self.vec_arrow = Vector2()
        self.half_dist = self.half_len - self.dir_arrow_rect.width//2
        self.centerx = self.rect.width // 2
        self.centery = self.rect.height // 2
        self.cool_down_l = 0
        self.cool_down_r = 0
        self.side = side

        self.place_dir_arrow()
        Sprites.robots.add(self)

    def move(self, move_dir, distance=None):
        if move_dir == Conf.FORWARD:
            # Move in current direction
            super().move(self.move_angle)
        elif move_dir == Conf.BACKWARD:
            # Rotate direction by 180 amd move forward
            super().move(self.move_angle + 180)
        elif move_dir == Conf.LEFT:
            # Prevent excessive updates to angle change for a single press
            dur = Frames.time() - self.cool_down_l
            if dur > Conf.COOLDOWN_TIME:
                self.move_angle -= Conf.DIR_OFFSET
                self.cool_down_l = Frames.time()
                self.place_dir_arrow()
                self.limit_angle()
        elif move_dir == Conf.RIGHT:
            dur = Frames.time() - self.cool_down_r
            if dur > Conf.COOLDOWN_TIME:
                self.move_angle += Conf.DIR_OFFSET
                self.cool_down_r = Frames.time()
                self.place_dir_arrow()
                self.limit_angle()

    def kick(self):
        for ball in Sprites.balls:
            self.vec.x = ball.rect.centerx - self.rect.centerx
            self.vec.y = ball.rect.centery - self.rect.centery
            dist, angle = self.vec.as_polar()
            self.limit_angle()

            if (
                    self.in_range(dist)
                    and
                    self.move_angle - Conf.DIR_OFFSET
                    < angle
                    < self.move_angle + Conf.DIR_OFFSET
            ):
                ball.get_kicked(speed=self.kick_speed(dist), angle=angle)
                ball.move_angle = angle

    def in_range(self, distance):
        if (
                self.half_len - Conf.HALF_RANGE
                < distance
                < self.half_len + Conf.HALF_RANGE
        ):
            return True

    @staticmethod
    def kick_speed(dist):
        speed = abs((0.0027*dist*dist)+(Conf.FORCE_LIMIT//3))
        if speed > Conf.FORCE_LIMIT:
            speed = Conf.FORCE_LIMIT
        return speed

    def place_dir_arrow(self):
        self.vec_arrow.from_polar((self.half_dist, self.move_angle))
        self.vec_arrow.x += self.half_dist
        self.vec_arrow.y += self.half_dist
        self.image = self.image_org.copy()
        self.image.blit(self.dir_arrow, self.vec_arrow)

    def update(self):
        if DoFlag.show_directions:
            self.draw_movement_line()


class Ball(BaseClass):
    def __init__(self, size=Conf.BALL_SIZE, pos=None, color=Conf.COLOR2):
        if pos is None:
            pos = (Conf.WIDTH//2, Conf.HEIGHT//2)
        super().__init__(size, pos=pos, color=color, text="B")
        Gen.last_goal_time = Frames.time()
        Sprites.balls.add(self)
        self.move_dist = 0  # Move distance
        self.move_angle = 0  # Degrees from positive x-axis
        self.do_move = False
        self.friction = Physics.FRICTION
        self.score = ScoreNum.get_inst()

        self.kick_time = 0
        self.max_time = 0
        self.mass = Physics.BALL_MASS
        self.f_normal = self.mass * Physics.G
        self.f_friction = self.f_normal * Physics.MU  # Force due to friction
        self.a_friction = self.f_friction / self.mass  # Acceleration  ||

        self.score_side = None
        self.score_time = None

    def check_bounds(self):
        if self.rect.top < 0 or self.rect.bottom > Conf.HEIGHT:
            self.move_dist -= Conf.WALL_PENALTY
            self.move_angle *= -1
            self.limit_angle()
            self.get_kicked(self.move_dist, self.move_angle)
        if self.rect.left < 0 or self.rect.right > Conf.WIDTH:
            self.move_dist -= Conf.WALL_PENALTY
            self.move_angle = -self.move_angle + 180
            self.limit_angle()
            self.get_kicked(self.move_dist, self.move_angle)
        super().check_bounds()

    def get_kicked(self, speed, angle):
        self.move_dist = speed
        self.move_angle = angle
        self.kick_time = Frames.time()
        self.max_time = speed / self.a_friction
        self.do_move = True

    def reset_record(self):
        self.score_side = None
        self.score_time = None

    def update(self):
        if DoFlag.show_directions:
            self.draw_movement_line()
        for goal in Sprites.goals:
            enough_dur = (Frames.time() - goal.last_touch) > 0.1
            if self.rect.colliderect(goal) and enough_dur:
                goal.last_touch = Frames.time()
                if goal.side == Conf.LEFT:
                    self.score_side = Conf.RIGHT
                    Score.right += 1
                else:
                    self.score_side = Conf.LEFT
                    Score.left += 1
                self.score_time = Frames.time() - Gen.last_goal_time
                self.score.update_score()
                rest_positions()

        if self.do_move:
            dur = Frames.time() - self.kick_time
            if dur < self.max_time:
                distance = 0.5 * self.move_dist * (self.max_time - dur)
                if distance < 2:
                    return
                self.move(self.move_angle, distance)
            else:
                self.do_move = False


class ScoreNum(pygame.sprite.Sprite):
    # This class stores the game score
    _inst = None

    @classmethod
    def get_inst(cls):
        # Used to the same instance to be available globally
        if cls._inst is None:
            cls._inst = cls()
        return cls._inst

    def __init__(self):
        super().__init__()

        # Create base image
        self.image = pygame.Surface((200, 30))
        self.image.fill(Conf.ALPHA_COLOR)  # Fill with color to be invisible
        self.image.set_colorkey(Conf.ALPHA_COLOR)  # Make color invisible
        self.rect = self.image.get_rect()

        # Set score position
        self.rect.y = 0
        self.rect.centerx = Conf.WIDTH//2

        # Create text for score
        self.font = pygame.font.SysFont('arial', 20)
        self.text = "LEFT 0 : RIGHT 0"
        self.text_render = self.font.render(self.text, True, Conf.BLACK)
        self.text_rect = self.text_render.get_rect()
        self.text_rect.center = (self.rect.width//2, self.rect.height//2)
        # Place text
        self.image.blit(self.text_render, self.text_rect)

        # Add to all sprites to allow being updated later
        Sprites.every.add(self)

    def update_score(self):
        self.image.fill(Conf.ALPHA_COLOR)  # Clear score box
        self.text = f"LEFT {Score.left} : RIGHT {Score.right}"  # Update text
        self.text_render = self.font.render(self.text, True, Conf.BLACK)
        self.text_rect = self.text_render.get_rect()
        self.text_rect.center = (self.rect.width//2, self.rect.height//2)
        print(f"time since last goal = {Frames.time() - Gen.last_goal_time}")
        Gen.last_goal_time = Frames.time()
        # Place text
        self.image.blit(self.text_render, self.text_rect)


class Goal(pygame.sprite.Sprite):
    _inst = {Conf.LEFT: None, Conf.RIGHT: None}

    @classmethod
    # Allow each goal to be accessible globally
    def get_inst(cls, side):
        if cls._inst[side] is None:
            cls._inst[side] = cls(side)
        return cls._inst[side]

    def __init__(self, side):
        super().__init__()
        # self.width, self.height = Conf.GOAL_SIZE
        self.image = pygame.Surface(Conf.GOAL_SIZE)
        if side == Conf.LEFT:
            self.color = Conf.COLOR_LEFT
        elif side == Conf.RIGHT:
            self.color = Conf.COLOR_RIGHT
        else:
            raise ValueError(
                f"Error side must either be '{Conf.LEFT}' or '{Conf.RIGHT}'"
                f"but {side} was recieved"
            )
        self.image.fill(self.color)
        self.side = side
        self.last_touch = 0  # Used to check for scoring

        self.rect = self.image.get_rect()
        self.rect.centery = Conf.HEIGHT // 2
        if side == Conf.LEFT:
            self.rect.x = 0
        else:
            self.rect.x = Conf.WIDTH - Conf.GOAL_SIZE[0]

        Sprites.goals.add(self)
        Sprites.every.add(self)


def rest_positions(robot_xy=None, ball_xy=None):
    # Get total score to know how many goals have been completed
    Score.total = Score.left + Score.right
    for robot in Sprites.robots:
        if robot_xy is not None:
            if Score.total > len(robot_xy):
                # Get random positions if list exhausted
                robot_xy = None
            else:
                # For each goal set the xy position
                robot.rect.centerx, robot.rect.centery = robot_xy[Score.total]
        if robot_xy is None:
            robot.rect.centery = random.randint(0, Conf.HEIGHT)
            if robot.side == Conf.LEFT:
                robot.rect.centerx = random.randint(0, Conf.WIDTH//2)
                robot.direction_angle = 0
                robot.place_dir_arrow()
            else:
                robot.rect.centerx = random.randint(Conf.WIDTH//2, Conf.WIDTH)
                robot.direction_angle = 180
                robot.place_dir_arrow()
            robot.check_bounds()

    for ball in Sprites.balls:
        if ball_xy is not None:
            if Score.total > len(ball_xy):
                # Get random positions if list exhausted
                ball_xy = None
            else:
                # For each goal set the xy position
                ball.rect.centerx, ball.rect.centery = ball_xy[Score.total]
        if ball_xy is None:
            offset = Conf.RBT_SIZE[0]
            ball.rect.centerx = random.randint(offset, Conf.WIDTH - offset)
            ball.rect.centery = random.randint(offset, Conf.HEIGHT - offset)
            ball.move_dist = 0

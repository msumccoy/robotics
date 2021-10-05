import time
import pygame
import random
import math
from pygame.math import Vector2

from config import Conf, Physics
from variables import PlayerCount, Score

all_sprites = pygame.sprite.Group()
robot_sprites = pygame.sprite.Group()
ball_sprites = pygame.sprite.Group()
goal_sprites = pygame.sprite.Group()


def rest_positions():
    for robot in robot_sprites:
        robot.rect.centery = random.randint(0, Conf.HEIGHT)
        if robot.side == Conf.LEFT:
            robot.rect.centerx = random.randint(0, Conf.WIDTH//2)
        else:
            robot.rect.centerx = random.randint(Conf.WIDTH//2, Conf.WIDTH)
            robot.direction_angle = math.pi
            robot.place_dir_arrow()
        robot.check_bounds()

    for ball in ball_sprites:
        ball.rect.centerx = Conf.WIDTH//2
        ball.rect.centery = Conf.HEIGHT//2
        ball.speed = 0

    time.sleep(1)


class ScoreNum(pygame.sprite.Sprite):
    _inst = None

    @classmethod
    def get_inst(cls):
        if cls._inst is None:
            cls._inst = cls()
        return cls._inst

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((200, 30))
        self.image.fill(Conf.ALPHA_COLOR)
        self.image.set_colorkey(Conf.ALPHA_COLOR)
        self.rect = self.image.get_rect()

        self.rect.y = 0
        self.rect.centerx = Conf.WIDTH//2

        self.font = pygame.font.SysFont('arial', 20)
        self.text = "LEFT 0 : RIGHT 0"
        self.text_render = self.font.render(self.text, True, Conf.BLACK)
        self.text_rect = self.text_render.get_rect()
        self.text_rect.center = (self.rect.width//2, self.rect.height//2)
        self.image.blit(self.text_render, self.text_rect)

        all_sprites.add(self)

    def update_score(self):
        self.image.fill(Conf.ALPHA_COLOR)
        self.text = f"LEFT {Score.left} : RIGHT {Score.right}"
        self.text_render = self.font.render(self.text, True, Conf.BLACK)
        self.text_rect = self.text_render.get_rect()
        self.text_rect.center = (self.rect.width//2, self.rect.height//2)
        self.image.blit(self.text_render, self.text_rect)


class Goal(pygame.sprite.Sprite):
    def __init__(self, side):
        super().__init__()
        self.height = int(Conf.HEIGHT / 3)
        self.width = 6
        self.image = pygame.Surface((self.width, self.height))
        if side == Conf.LEFT:
            self.color = Conf.COLOR_LEFT
        elif side == Conf.RIGHT:
            self.color = Conf.COLOR_RIGHT
        else:
            raise ValueError(
                f"Error side must either be '{Conf.LEFT}' or '{Conf.RIGHT}'"
            )
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.side = side
        self.last_touch = 0

        self.rect.centery = int(Conf.HEIGHT / 2)
        if side == Conf.LEFT:
            self.rect.x = 5 - self.width
        else:
            self.rect.x = Conf.WIDTH - 5

        goal_sprites.add(self)
        all_sprites.add(self)


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
        self.distance = 5
        self.size = size
        self.half_len = size[0]//2
        all_sprites.add(self)

    def move(self, move_dir, distance=None):
        if distance is None:
            distance = self.distance
        self.vec.from_polar((distance, move_dir))
        self.rect.centerx += self.vec.x
        self.rect.centery += self.vec.y
        self.check_bounds()

    def check_bounds(self):
        if self.rect.top < 0:
            self.rect.y = 0
        elif self.rect.bottom > Conf.HEIGHT:
            self.rect.y = Conf.HEIGHT - self.rect.height
        if self.rect.left < 0:
            self.rect.x = 0
        elif self.rect.right > Conf.WIDTH:
            self.rect.x = Conf.WIDTH - self.rect.width

    def change_speed(self, direction):
        if direction == Conf.UP:
            self.distance += 1
        elif direction == Conf.DOWN:
            self.distance -= 1

    @staticmethod
    def deg_to_rad(angle):
        # TODO: potentially to delete
        return angle
        return (angle * math.pi) / 180

    @staticmethod
    def rad_to_deg(angle):
        return (angle * 180) / math.pi


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
            self.direction_angle = 0
        elif side == Conf.RIGHT:
            color = Conf.COLOR_RIGHT
            PlayerCount.left += 1
            if pos is None:
                pos = (
                    random.randint(Conf.WIDTH//2, Conf.WIDTH),
                    random.randint(0, Conf.HEIGHT)
                )
            self.direction_angle = math.pi
        else:
            raise ValueError(
                f"Error side must either be '{Conf.LEFT}' or '{Conf.RIGHT}'"
            )
        super().__init__(size, pos=pos, text="RBT", color=color)
        self.check_bounds()
        self.image_org = self.image.copy()
        arrow_size = (size[0] / 5, size[1] / 5)
        self.dir_arrow = pygame.Surface(arrow_size)
        self.dir_arrow.fill(Conf.BLACK)
        self.dir_arrow_rect = self.dir_arrow.get_rect()
        self.dir_arrow_offset = (
            self.dir_arrow_rect.width / 2,
            self.dir_arrow_rect.height / 2
        )
        self.centerx, self.centery = self.rect.width / 2, self.rect.height / 2
        self.cool_down_l = 0
        self.cool_down_r = 0
        self.DIRECTION_OFFSET = self.deg_to_rad(Conf.DIRECTION_OFFSET)
        self.side = side

        self.place_dir_arrow()
        robot_sprites.add(self)

    def move(self, move_dir, speed=None):
        if move_dir == Conf.FORWARD:
            # Move in current direction
            super().move(self.direction_angle)
        elif move_dir == Conf.BACKWARD:
            # Rotate direction by 180 amd move forward
            super().move(self.direction_angle+180)
        elif move_dir == Conf.LEFT:
            # Prevent excessive updates to angle change for a single press
            dur = time.time() - self.cool_down_l
            if dur > Conf.COOLDOWN_TIME:
                self.direction_angle -= self.DIRECTION_OFFSET * 0.5
                self.cool_down_l = time.time()
                self.place_dir_arrow()
        elif move_dir == Conf.RIGHT:
            dur = time.time() - self.cool_down_r
            if dur > Conf.COOLDOWN_TIME:
                self.direction_angle += self.DIRECTION_OFFSET * 0.5
                self.cool_down_r = time.time()
                self.place_dir_arrow()

    def kick(self):
        # TODO: finish fixing
        for ball in ball_sprites:
            self.vec.x = ball.rect.centerx - self.rect.centerx
            self.vec.y = ball.rect.centery - self.rect.centery
            dist, angle = self.vec.as_polar()

            if (
                    self.half_len - Conf.HALF_RANGE
                    < dist
                    < self.half_len + Conf.HALF_RANGE
                    and
                    self.direction_angle - Conf.DIRECTION_OFFSET
                    < angle
                    < self.direction_angle + Conf.DIRECTION_OFFSET
            ):
                print("GOOD") # Now kick the ball
            else:
                print(dist, angle, self.direction_angle)
            return
            if distx > 0 and disty > 0 or distx > 0 > disty:
                # Quadrant 1 or Quadrant 4
                angle = math.atan(disty / distx)
            else:  # Quadrant 2 or Quadrant 3
                if distx == 0:
                    if disty < 0:
                        angle = 3 * math.pi / 2
                    else:
                        angle = math.pi / 2
                else:
                    angle = math.atan(disty / distx) + math.pi
            if abs(self.direction_angle - angle) > self.DIRECTION_OFFSET:
                new_da = self.limit_angle(self.direction_angle + math.pi)
                new_a = self.limit_angle(angle + math.pi)
                if abs(new_da - new_a) > self.DIRECTION_OFFSET:
                    continue
            ball.get_kicked(speed=self.kick_speed(dist), angle=angle)
            ball.speed = self.kick_speed(dist)
            ball.move_angle = angle

    @staticmethod
    def kick_speed(dist):
        speed = abs(dist*dist - 23)
        if speed > Conf.FORCE_LIMIT:
            speed = Conf.FORCE_LIMIT
        return speed

    def place_dir_arrow(self):
        center_dist = self.half_len - self.dir_arrow_rect.width//2
        self.vec.from_polar((center_dist, self.direction_angle))
        self.vec.x += center_dist
        self.vec.y += center_dist
        self.image = self.image_org.copy()
        self.image.blit(self.dir_arrow, self.vec)


class Ball(BaseClass):
    def __init__(self, size=Conf.BALL_SIZE, pos=None, color=Conf.COLOR2):
        if pos is None:
            pos = (Conf.WIDTH//2, Conf.HEIGHT//2)
        super().__init__(size, pos=pos, color=color, text="B")
        ball_sprites.add(self)
        self.speed = 0
        self.move_angle = 0  # Degrees from positive x-axis
        self.do_move = False
        self.friction = Conf.FRICTION_DECREASE
        self.score = ScoreNum.get_inst()

        self.kick_time = 0
        self.max_time = 0
        self.mass = Physics.BALL_MASS
        self.f_normal = self.mass * Physics.G
        self.f_friction = self.f_normal * Physics.MU  # Force due to friction
        self.a_friction = self.f_friction / self.mass  # Acceleration  ||

    def check_bounds(self):
        if self.rect.top < 0 or self.rect.bottom > Conf.HEIGHT:
            self.speed -= Conf.WALL_PENALTY
            self.move_angle *= -1
        if self.rect.left < 0 or self.rect.right > Conf.WIDTH:
            self.speed -= Conf.WALL_PENALTY
            self.move_angle = math.pi - self.move_angle
        super().check_bounds()

    def get_kicked(self, speed, angle):
        self.speed = speed
        self.move_angle = angle
        self.kick_time = time.time()
        self.max_time = speed / self.a_friction
        self.do_move = True

    def update(self):
        for goal in goal_sprites:
            enough_dur = (time.time() - goal.last_touch) > 0.1
            if self.rect.colliderect(goal) and enough_dur:
                goal.last_touch = time.time()
                if goal.side == Conf.LEFT:
                    Score.right += 1
                else:
                    Score.left += 1
                self.score.update_score()
                rest_positions()

        if self.do_move:
            dur = time.time() - self.kick_time
            if dur < self.max_time:
                distance = 0.5 * self.speed * (self.max_time - dur)
                if distance < 2:
                    return
                self.move(self.move_angle, distance)
            else:
                self.do_move = False

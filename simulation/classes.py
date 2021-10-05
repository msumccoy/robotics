import time
import pygame
import random
import math

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
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.distance = 5
        self.size = size
        all_sprites.add(self)

    def move(self, move_dir, distance=None):
        if distance is None:
            distance = self.distance
        try:
            angle = move_dir
            self.rect.x += distance * math.cos(angle)
            self.rect.y -= distance * math.sin(angle)
            # print(f"self-{self}\ndist: {distance} angle{(move_dir * 180) / math.pi} x:{self.rect.x} y:{self.rect.y}")
        except TypeError:
            pass
        if move_dir == Conf.UP:
            self.rect.y -= distance
        elif move_dir == Conf.DOWN:
            self.rect.y += distance
        elif move_dir == Conf.LEFT:
            self.rect.x -= distance
        elif move_dir == Conf.RIGHT:
            self.rect.x += distance
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
            super().move(self.direction_angle)
        elif move_dir == Conf.BACKWARD:
            super().move(self.direction_angle, distance=-self.distance)
        elif move_dir == Conf.LEFT:
            dur = time.time() - self.cool_down_l
            if dur > Conf.COOLDOWN_TIME:
                self.direction_angle += self.DIRECTION_OFFSET * 0.5
                self.cool_down_l = time.time()
                self.place_dir_arrow()
                self.limit_angle()
        elif move_dir == Conf.RIGHT:
            dur = time.time() - self.cool_down_r
            if dur > Conf.COOLDOWN_TIME:
                self.direction_angle -= self.DIRECTION_OFFSET * 0.5
                self.cool_down_r = time.time()
                self.place_dir_arrow()
                self.limit_angle()

    def limit_angle(self, angle=None):
        if angle is None:
            angle = self.direction_angle
            default = True
        else:
            default = False
        pi_twice = 2 * math.pi
        while angle < 0:
            angle += pi_twice
        while angle > pi_twice:
            angle -= pi_twice
        if default:
            self.direction_angle = angle
        else:
            return angle

    def kick(self):
        for ball in ball_sprites:
            distx = ball.rect.centerx - self.rect.centerx
            disty = -(ball.rect.centery - self.rect.centery)
            dist = (
                math.sqrt((distx * distx) + (disty * disty))
                - (self.rect.width / 2)
                - (ball.rect.width / 2)
            )
            if (
                    dist < 0 and abs(dist) > Conf.KICK_RANGE
                    or 0 < dist and dist > Conf.KICK_RANGE - Conf.DIST_OFFSET
            ):
                continue
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
            angle = self.limit_angle(angle)
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
        x = self.centerx + (math.cos(self.direction_angle) * self.rect.width / 2)
        y = self.centery - (math.sin(self.direction_angle) * self.rect.height / 2)
        x -= self.dir_arrow_offset[0]
        y -= self.dir_arrow_offset[1]
        if x + self.dir_arrow_rect.right > self.rect.width:
            x = self.rect.width - self.dir_arrow_rect.width
        elif x < 0:
            x = 0
        if y + self.dir_arrow_rect.bottom > self.rect.height:
            y = self.rect.height - self.dir_arrow_rect.height
        elif y < 0:
            y = 0
        self.image = self.image_org.copy()
        self.image.blit(self.dir_arrow, (x, y))


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

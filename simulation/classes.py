import time
import pygame
import random
import math

from config import Conf


all_sprites = pygame.sprite.Group()
robot_sprites = pygame.sprite.Group()
ball_sprites = pygame.sprite.Group()


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
        self.speed = 5
        self.size = size
        all_sprites.add(self)

    def move(self, move_dir, speed=None):
        if speed is None:
            speed = self.speed
        try:
            angle = move_dir
            self.rect.x += speed * math.cos(angle)
            self.rect.y -= speed * math.sin(angle)
        except TypeError:
            pass
        if move_dir == Conf.UP:
            self.rect.y -= speed
        elif move_dir == Conf.DOWN:
            self.rect.y += speed
        elif move_dir == Conf.LEFT:
            self.rect.x -= speed
        elif move_dir == Conf.RIGHT:
            self.rect.x += speed
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
            self.speed += 1
        elif direction == Conf.DOWN:
            self.speed -= 1

    @staticmethod
    def deg_to_rad(angle):
        return (angle * math.pi) / 180

    @staticmethod
    def rad_to_deg(angle):
        return (angle * 180) / math.pi


class Robot(BaseClass):
    def __init__(self, size=Conf.RBT_SIZE, pos=(0, 0), img=None):
        super().__init__(size, pos=pos, text="RBT")
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
        self.direction_angle = 0
        self.cool_down_l = 0
        self.cool_down_r = 0
        self.DIRECTION_OFFSET = self.deg_to_rad(Conf.DIRECTION_OFFSET)

        self.place_dir_arrow()
        robot_sprites.add(self)

    def move(self, move_dir, speed=None):
        if move_dir == Conf.FORWARD:
            super().move(self.direction_angle)
        elif move_dir == Conf.BACKWARD:
            super().move(self.direction_angle, speed=-self.speed)
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
            ball.speed = self.kick_force(dist)
            ball.move_angle = angle

    @staticmethod
    def kick_force(dist):
        dist = 2 * dist - 1
        force = abs(dist*dist - 23)
        if force > Conf.FORCE_LIMIT:
            force = Conf.FORCE_LIMIT
        return force

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
            pos = (
                random.randint(0, Conf.WIDTH), random.randint(0, Conf.HEIGHT)
            )
        super().__init__(size, pos=pos, color=color, text="B")
        ball_sprites.add(self)
        self.speed = 0
        self.move_angle = 0  # Degrees from positive x-axis
        self.friction = Conf.FRICTION_DECREASE

    def check_bounds(self):
        if self.rect.top < 0 or self.rect.bottom > Conf.HEIGHT:
            self.speed -= Conf.WALL_PENALTY
            self.move_angle *= -1
        if self.rect.left < 0 or self.rect.right > Conf.WIDTH:
            self.speed -= Conf.WALL_PENALTY
            self.move_angle = math.pi - self.move_angle
        super().check_bounds()

    def update(self):
        if self.speed > 0:
            self.move(self.move_angle)
            self.speed += self.friction
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
            angle = self.deg_to_rad(move_dir)
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
        elif self.rect.left < 0:
            self.rect.x = 0
        elif self.rect.right > Conf.WIDTH:
            self.rect.x = Conf.WIDTH - self.rect.width

    def change_speed(self, direction):
        if direction == Conf.UP:
            self.speed += 1
        elif direction == Conf.DOWN:
            self.speed -= 1

    def deg_to_rad(self, angle):
        angle = (angle * math.pi) / 180
        return angle


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
        self.direction_angle = 0
        self.cool_down_l = 0
        self.cool_down_r = 0
        robot_sprites.add(self)

    def move(self, move_dir, speed=None):
        if move_dir == Conf.FORWARD:
            super().move(self.direction_angle)
        elif move_dir == Conf.BACKWARD:
            super().move(self.direction_angle, speed=-self.speed)
            self.image.fill(Conf.BLACK)
        elif move_dir == Conf.LEFT:
            dur = time.time() - self.cool_down_l
            self.image = self.image_org.copy()
            if dur > Conf.COOLDOWN_TIME:
                self.direction_angle += 15
                self.cool_down_l = time.time()
        elif move_dir == Conf.RIGHT:
            dur = time.time() - self.cool_down_r
            if dur > Conf.COOLDOWN_TIME:
                self.direction_angle -= 15
                self.cool_down_r = time.time()

    def kick(self):
        for ball in ball_sprites:
            ball.speed = 10
            print(ball)

    def update(self):
        self.place_dir_arrow()

    def place_dir_arrow(self):
        angle = self.deg_to_rad(self.direction_angle)
        x = math.cos(angle) * self.rect.width
        if x + self.dir_arrow_rect.right > self.rect.width:
            x = self.rect.width - self.dir_arrow_rect.width
        elif x < 0:
            x = self.dir_arrow_offset[1]
        y = -(math.sin(angle) * self.rect.height)
        if y + self.dir_arrow_rect.bottom > self.rect.height:
            y = self.dir_arrow_rect.bottom - self.dir_arrow_rect.height
        elif y < 0:
            y = 0
        print(y)
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
        self.friction = -0.3

    def update(self):
        if self.speed != 0:
            self.move(self.move_angle)
            self.speed += self.friction
            if self.speed < 0:
                self.speed = 0

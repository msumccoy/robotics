import pygame
import random

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

    def move(self, move_type, speed=None):
        if speed is None:
            speed = self.speed
        if move_type == Conf.UP and self.rect.top > 0:
            self.rect.y -= speed
        elif move_type == Conf.DOWN and self.rect.bottom < Conf.HEIGHT:
            self.rect.y += speed
        elif move_type == Conf.LEFT and self.rect.left > 0:
            self.rect.x -= speed
        elif move_type == Conf.RIGHT and self.rect.right < Conf.WIDTH:
            self.rect.x += speed

    def change_speed(self, direction):
        if direction == Conf.UP:
            self.speed += 1
        elif direction == Conf.DOWN:
            self.speed -= 1


class Robot(BaseClass):
    def __init__(self, size=Conf.RBT_SIZE, pos=(0, 0), img=None):
        super().__init__(size, pos=pos, text="RBT")
        robot_sprites.add(self)

    def kick(self):
        print(ball_sprites)
        for a in ball_sprites:
            print(a)


class Ball(BaseClass):
    def __init__(self, size=Conf.BALL_SIZE, pos=None, color=Conf.COLOR2):
        if pos is None:
            pos = (
                random.randint(0, Conf.WIDTH), random.randint(0, Conf.HEIGHT)
            )
        super().__init__(size, pos=pos, color=color, text="B")
        ball_sprites.add(self)

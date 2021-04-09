import pygame
import random

from config import Conf


class BaseClass(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(Conf.ALPHA_COLOR)
        self.image.set_colorkey(Conf.ALPHA_COLOR)
        self.rect = self.image.get_rect()
        pygame.draw.circle(
            self.image, Conf.COLOR1, self.rect.center, self.rect.width//2
        )
        self.font = pygame.font.SysFont('arial', 10)
        text = self.font.render("B", True, Conf.BLACK)
        text_rect = text.get_rect()
        text_rect.center = (self.rect.width//2, self.rect.height//2)
        self.image.blit(text, text_rect)
        self.speed = 5
        self.size = size

    def move(self, move_type):
        if move_type == Conf.UP and self.rect.top > 0:
            self.rect.y -= self.speed
        elif move_type == Conf.DOWN and self.rect.bottom < Conf.HEIGHT:
            self.rect.y += self.speed
        elif move_type == Conf.LEFT and self.rect.left > 0:
            self.rect.x -= self.speed
        elif move_type == Conf.RIGHT and self.rect.right < Conf.WIDTH:
            self.rect.x += self.speed

    def change_speed(self, direction):
        if direction == Conf.UP:
            self.speed += 1
        elif direction == Conf.DOWN:
            self.speed -= 1


class Robot(BaseClass):
    def __init__(self, size=Conf.RBT_SIZE):
        super().__init__(size)
        pygame.draw.circle(
            self.image, Conf.COLOR1, self.rect.center, self.rect.width // 2
        )
        text = self.font.render("R", True, Conf.BLACK)
        text_rect = text.get_rect()
        text_rect.center = (self.rect.width//2, self.rect.height//2)
        self.image.blit(text, text_rect)

    def move(self, move_type):
        super().move(move_type)
        super().move(move_type)


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        pass

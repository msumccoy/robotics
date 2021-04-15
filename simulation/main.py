import sys
import pygame
import random

from config import Conf
from classes import Robot, Ball
from classes import all_sprites, robot_sprites, ball_sprites


def main():
    pygame.init()

    screen = pygame.display.set_mode(Conf.WIN_SIZE)
    background = pygame.Surface(Conf.WIN_SIZE).convert()
    background.fill(Conf.WHITE)
    screen.blit(background, (0, 0))

    robot0 = Robot(pos=(50, 50))
    ball0 = Ball()
    ball1 = Ball()
    clock = pygame.time.Clock()
    while True:
        clock.tick(Conf.FPS)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            robot0.move(Conf.UP)
        if keys[pygame.K_DOWN]:
            robot0.move(Conf.DOWN)
        if keys[pygame.K_RIGHT]:
            robot0.move(Conf.RIGHT)
        if keys[pygame.K_LEFT]:
            robot0.move(Conf.LEFT)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    robot0.kick()

        screen.fill(Conf.WHITE)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.update()


if __name__ == '__main__':
    main()






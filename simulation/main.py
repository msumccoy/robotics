"""
boundary limits
goal limit
have side
record score
robot and robot collision
robot and ball collision
robot kick ball

"""
import sys
import pygame
import random

from config import Conf
from classes import Robot, Ball, Goal, ScoreNum
from classes import all_sprites, robot_sprites, ball_sprites, goal_sprites


def main():
    print(
        "Take note that this game is primarily designed for one robot and "
        "one ball.\n"
        "While the game does have the functionality to have multiple balls "
        "and multiple robots all functionality is not implemented\n"
        "Namely robot collision, and ball collision (for blocking balls "
        "kicked by other players)"
    )
    pygame.init()

    screen = pygame.display.set_mode(Conf.WIN_SIZE)
    background = pygame.Surface(Conf.WIN_SIZE).convert()
    background.fill(Conf.WHITE)
    screen.blit(background, (0, 0))

    robot0 = Robot(side=Conf.LEFT)
    ball0 = Ball()
    goal_left = Goal(Conf.LEFT)
    goal_right = Goal(Conf.RIGHT)
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






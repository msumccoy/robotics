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
from sim_objects import Robot, Ball, Goal, ScoreNum

from variables import ExitCtr, DoFlag, Sprites, Gen
from controls import Controllers


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

    # Set up simulation window
    Gen.screen = pygame.display.set_mode(Conf.WIN_SIZE)
    background = pygame.Surface(Conf.WIN_SIZE).convert()
    background.fill(Conf.WHITE)
    Gen.screen.blit(background, (0, 0))

    # Create the robot, ball, and goals
    robots = [Robot(side=Conf.LEFT)]
    # robots = [Robot(side=Conf.RIGHT)]
    balls = [Ball()]
    goal_left = Goal(Conf.LEFT)
    goal_right = Goal(Conf.RIGHT)

    controller = Controllers(robots[0])

    # Create clock for consistent loop intervals
    clock = pygame.time.Clock()
    while ExitCtr.gen:
        # Control loop intervals
        clock.tick(Conf.FPS)
        Gen.screen.fill(Conf.WHITE)

        # Control robot
        controller.manual_control()
        if DoFlag.auto_calc:
            controller.calculated_control()

        # Update game state
        Sprites.every.update()
        Sprites.every.draw(Gen.screen)
        pygame.display.update()


if __name__ == '__main__':
    main()






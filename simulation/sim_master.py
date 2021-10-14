import pygame

from config import Conf
from controls import Controllers
from variables import Gen, ExitCtr, Frames, Sprites, DoFlag
from sim_objects import Robot, Ball, Goal


class SimMaster:
    def __init__(self, index):
        self.index = index

        self.robots = []
        self.balls = []
        self.goals = []

        self.controller = None
        self.clock = None

    def start(self):
        pygame.init()
        # Set up simulation window
        Gen.screen = pygame.display.set_mode(Conf.WIN_SIZE)
        background = pygame.Surface(Conf.WIN_SIZE).convert()
        background.fill(Conf.WHITE)
        Gen.screen.blit(background, (0, 0))

        # Create the robot, ball, and goals
        self.robots = [Robot(side=Conf.LEFT)]
        self.balls = [Ball()]
        self.goals = [Goal(Conf.LEFT), Goal(Conf.RIGHT)]

        self.controller = Controllers(self.robots[0])

        # Create clock for consistent loop intervals
        self.clock = pygame.time.Clock()
        while ExitCtr.gen:
            Gen.screen.fill(Conf.WHITE)  # Reset screen for fresh drawings
            # Control loop intervals
            self.clock.tick(Conf.FPS)

            # Control robot
            self.controller.manual_control()
            self.controller.check_score()
            if DoFlag.auto_calc:
                self.controller.calculated_control()

            # Update game state
            Sprites.every.update()
            Sprites.every.draw(Gen.screen)
            pygame.display.update()
            Frames.update()

        self.controller.save()
        pygame.quit()

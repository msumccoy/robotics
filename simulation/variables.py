import time
from config import Conf


class Score:
    left = 0
    right = 0
    total = 0


class PlayerCount:
    left = 0
    right = 0


class ExitCtr:
    gen = True


class DoFlag:
    auto_calc = True
    show_vectors = False
    show_directions = False


class Gen:
    screen = None
    key_a_time = 0
    key_b_time = 0
    key_c_time = 0
    last_goal_time = 0


class Sprites:
    from pygame.sprite import Group
    every = Group()
    robots = Group()
    balls = Group()
    goals = Group()


class Frames:
    """This class is used to handle time based operations"""
    _DESIGNED_FPS = Conf.FPS
    _DESIGNED_FPS = 30

    _frames = 0
    _fps = Conf.FPS
    _start = time.time()

    @classmethod
    def update(cls):
        cls._frames += 1

    @classmethod
    def frames(cls):
        return cls._frames

    @classmethod
    def time(cls):
        time_passed = cls._frames / cls._DESIGNED_FPS  # frame * s/frame
        return time_passed

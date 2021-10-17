import time
from config import Conf


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
    # _DESIGNED_FPS = Conf.FPS
    _DESIGNED_FPS = 30

    _frames = 0
    _fps = Conf.FPS
    _calc_fps = 0
    _fps_sum = 0
    _fps_list = []
    _list_len = 30 * Conf.FPS
    _start = time.time()
    _last = time.time()

    @classmethod
    def update(cls):
        cls._frames += 1
        tmps_fps = 1 / (time.time() - cls._last)
        cls._fps_list.append(tmps_fps)
        cls._fps_sum += tmps_fps
        if len(cls._fps_list) > cls._list_len:
            tmps = cls._fps_list.pop(0)
            cls._fps_sum -= tmps
            cls._calc_fps = cls._fps_sum / cls._list_len
        else:
            cls._calc_fps = cls._fps_sum / len(cls._fps_list)
        cls._last = time.time()

    @classmethod
    def frames(cls):
        return cls._frames

    @classmethod
    def real_time(cls):
        return time.time() - cls._start

    @classmethod
    def fps(cls):
        return cls._calc_fps

    @classmethod
    def time(cls):
        time_passed = cls._frames / cls._DESIGNED_FPS  # frame * s/frame
        return time_passed

class Score:
    left = 0
    right = 0


class PlayerCount:
    left = 0
    right = 0


class ExitCtr:
    gen = True


class DoFlag:
    auto_calc = True
    chan = False


class Gen:
    key_a_pressed = 0


class Sprites:
    from pygame.sprite import Group
    every = Group()
    robots = Group()
    balls = Group()
    goals = Group()

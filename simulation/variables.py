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
    temp_b = False


class Gen:
    screen = None
    key_a_pressed = 0
    key_b_pressed = 0
    last_goal_time = 0


class Sprites:
    from pygame.sprite import Group
    every = Group()
    robots = Group()
    balls = Group()
    goals = Group()

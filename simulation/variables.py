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

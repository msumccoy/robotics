class Conf:
    FPS = 30
    WIN_SIZE = WIDTH, HEIGHT = 600, 400
    RBT_SIZE = [50] * 2
    BALL_SIZE = [10, 10]
    MOVE_VAL = 2
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    COLOR1 = (0, 255, 125)
    COLOR2 = (255, 0, 125)
    COLOR3 = (125, 125, 125)
    COLOR_LEFT = (0, 255, 125)
    COLOR_RIGHT = (255, 125, 0)
    ALPHA_COLOR = (156, 34, 87)

    ACCEPT = 0
    UD_UPPER = 1
    UD_LOWER = 2
    LR_LEFT = 1
    LR_RIGHT = 2

    UP = FORWARD = 'up or forward'
    DOWN = BACKWARD = 'down or backward'
    LEFT = 'left'
    RIGHT = 'right'

    COOLDOWN_TIME = .015
    KICK_RANGE = 10  # Distance unit
    DIRECTION_OFFSET = 10  # Degrees
    DIST_OFFSET = KICK_RANGE / 3  # Degrees
    FORCE_LIMIT = 4
    WALL_PENALTY = 1
    FRICTION_DECREASE = -0.3  # Must be negative


class Physics:
    G = 9.81
    MU = 0.1
    BALL_MASS = 0.1  # Kilograms

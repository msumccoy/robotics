class Conf:
    X = 0  # used for coordinates
    Y = 1  # used for coordinates
    NUM_PROC = 2
    FPS = 300
    WIN_SIZE = WIDTH, HEIGHT = 600, 400
    PADDING = 200
    ORIGIN = (PADDING // 2, PADDING // 2)  # X, Y
    CENTER = ((WIDTH + PADDING) // 2, (HEIGHT + PADDING) // 2)  # X, Y
    FIELD_RIGHT = ORIGIN[X] + WIDTH
    FIELD_BOT = ORIGIN[Y] + HEIGHT
    RBT_SIZE = [50] * 2
    BALL_SIZE = [10] * 2
    GOAL_SIZE = [6, HEIGHT // 3]  # [width, height]
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
    HALF_RANGE = 10  # Distance unit
    DIR_OFFSET = 5  # Degrees
    FORCE_LIMIT = 4
    WALL_PENALTY = .5
    FRICTION_DECREASE = -0.3  # Must be negative

    DEGREE = "degree"

    CSV = "csv_files"


class Physics:
    G = 9.81
    MU = 0.1
    BALL_MASS = 0.1  # Kilograms
    FRICTION = -0.3


class GS:  # Name to be changed
    ROBOT_START = "robot_start"
    BALL_START = "ball_start"
    TIME_TO_SCORE = "time"
    SIDE_SCORE = "side"

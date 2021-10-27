class Conf:
    X = 0  # used for coordinates
    Y = 1  # used for coordinates
    NUM_PROC = 1  # Number of processes to run
    FPS = 30  # The desired frames per second
    WIN_SIZE = WIDTH, HEIGHT = 600, 400  # Size of the window
    PADDING = 200  # The space around the soccer field (top/bottom and sides
    ORIGIN = (PADDING // 2, PADDING // 2)  # X, Y
    CENTER = ((WIDTH + PADDING) // 2, (HEIGHT + PADDING) // 2)  # X, Y
    FIELD_RIGHT = ORIGIN[X] + WIDTH  # Right most edge of field
    FIELD_BOT = ORIGIN[Y] + HEIGHT  # Lowest edge of field
    RBT_SIZE = [50] * 2  # Size of the robot
    BALL_SIZE = [10] * 2  # Size of the ball
    GOAL_SIZE = [6, HEIGHT // 3]  # [width, height]

    # Colors for display purposes
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    COLOR1 = (0, 255, 125)
    COLOR2 = (255, 0, 125)
    COLOR3 = (125, 125, 125)
    COLOR_LEFT = (0, 255, 125)
    COLOR_RIGHT = (255, 125, 0)
    ALPHA_COLOR = (156, 34, 87)  # Color to be seen as invisible

    UP = FORWARD = 'up or forward'
    DOWN = BACKWARD = 'down or backward'
    LEFT = 'left'
    RIGHT = 'right'

    VISION_THETA = 120  # Viewing angle directly in front robot
    KICK_COOLDOWN = 0.5
    CD_TIME = .15  # Used to prevent excessive activations
    HALF_RANGE = 10  # Half kick range
    CLOSE_RANGE = HALF_RANGE * 5  # To determine if robot was "close" to ball
    DIR_OFFSET = 5  # Angle offset
    MOVE_DIST = 5  # Default move distance
    FORCE_LIMIT = 4  # Max kick limit
    WALL_PENALTY = .5
    FRICTION_DECREASE = -0.3  # Must be negative

    DEGREE = "degree"
    CSV_FOLDER = "csv_files"

    # Neural net constants
    DIRECTION = "Direction"
    THETA = "Theta"
    DIST = "Distance"
    KICK = "Kick"
    CONT = "Continue"


class Physics:
    G = 9.81
    MU = 0.1
    BALL_MASS = 0.1  # Kilograms
    FRICTION = -0.3


class GS:  # Name to be changed  # Used for csv file to save game state
    ROBOT_START = "robot_start"
    BALL_START = "ball_start"
    TIME_TO_SCORE = "time"
    SIDE_SCORE = "side"
    METHOD = "method"

    # Method types
    TYPE_MAN = "manual/calculated"
    TYPE_NET = "network"


class FrameStepReturn:
    """
    This function is used with sim_master.SimMaster.frame_step to denote index
    of return values in numpy array
    """
    NUM_VAL = 21
    X = 0
    Y = 1
    BALL_FLAG = 2
    BALL_THETA = 3
    BALL_DIST = 4
    OWN_GOAL_THETA = 5
    OWN_GOAL_DIST = 6
    OPP_GOAL_THETA = 7
    OPP_GOAL_DIST = 8
    IS_KICK_SUCCESS = 9
    IS_KICK_ACCURATE = 10
    IS_KICKING = 11
    IS_MOVING = 12
    IS_BALL_MOVED = 13
    IS_GOAL_SCORED = 14
    TIME = 15
    ACT_DIR = 16
    ACT_THETA = 17
    ACT_DIST = 18
    ACT_KICK = 19
    ACT_CONT = 20

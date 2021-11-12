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

    HALF_VIS_THETA = 60  # Half the viewing angle directly in front robot
    KICK_COOLDOWN = 0.5
    CD_TIME = .5  # Used to prevent excessive activations
    HALF_RANGE = 10  # Half kick range
    CLOSE_RANGE = HALF_RANGE * 5  # To determine if robot was "close" to ball
    DIR_OFFSET = 15  # Angle offset: Should be set at 15 for Neural network
    MOVE_DIST = 5  # Default move distance: Should be 5
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
    TYPE_MAN = "man_calc"
    TYPE_NET = "network"


class FrameStepReturn:
    """
    This function is used with sim_master.SimMaster.frame_step to denote index
    of return values in numpy array
    """
    NUM_VAL = 21
    X = 0  # Robot x position
    Y = 1  # Robot y position
    BALL_FLAG = 2  # Ball seen
    BALL_THETA = 3  # Angle from robot to ball
    BALL_DIST = 4  # Distance to ball
    OWN_GOAL_THETA = 5  # Angle to own goal center
    OWN_GOAL_DIST = 6  # Distance to own goal center
    OPP_GOAL_THETA = 7  # Angle to target goal center
    OPP_GOAL_DIST = 8  # Distance to target goal
    IS_KICK_SUCCESS = 9  # If kick hit the ball
    IS_KICK_ACCURATE = 10  # If ball hit close to the goal
    IS_KICKING = 11  # If robot is curretnly kicking
    IS_MOVING = 12  # If robot is moving
    IS_BALL_MOVED = 13  # If ball moved relative to robot
    IS_GOAL_SCORED = 14  # If the goal was scored
    TIME = 15  # Current time (relative to frames)
    ACT_DIR = 16  # Action direction (move direction, left or right)
    ACT_THETA = 17  # Action theta (move angle
    ACT_DIST = 18  # Action move distance
    ACT_KICK = 19  # Action kick
    ACT_CONT = 20  # Action continue (if to continue)

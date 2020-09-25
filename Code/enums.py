"""
Kuwin Wyke
Midwestern State University

This module contains discrete types used within this project
"""
from enum import Enum


class RobotType(Enum):
    HUMAN = 0
    SPIDER = 1


class RobotCMD(Enum):
    TURN_LEFT = 0
    TURN_RIGHT = 1
    FORWARD = 2
    BACK = 3
    FORWARD_CONT = 4
    BACK_CONT = 5
    SIDE_STEP_LEFT = 6
    SIDE_STEP_RIGHT = 7
    KICK_LEFT = 8
    KICK_RIGHT = 9
    BACK_KICK = 10


class LensType(Enum):
    SINGLE = 0
    DOUBLE = 1


class DistType(Enum):
    MAIN = 0
    LEFT = 1
    RIGHT = 2


class ObjDist(Enum):
    AVG = 0
    LOCATION = 1
    SUM = 2
    COUNT = 3
    LAST_SEEN = 4
    IS_FOUND = 5
    LIST = 6


if __name__ == "__main__":
    pass

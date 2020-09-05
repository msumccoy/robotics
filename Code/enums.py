"""
Kuwin Wyke
Midwestern State University

This module contains discrete types used within this project
"""
from enum import Enum


class RobotType(Enum):
    HUMAN = 0
    SPIDER = 1


class LensType(Enum):
    SINGLE = 0
    DOUBLE = 1


class DistType(Enum):
    MAIN = 0
    LEFT = 1
    RIGHT = 2


class ObjDist(Enum):
    AVG = 0
    SUM = 1
    COUNT = 2
    LAST_SEEN = 3
    IS_FOUND = 4
    LIST = 5


if __name__ == "__main__":
    pass

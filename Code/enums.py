"""
Kuwin Wyke
Midwestern State University

This module contains discrete types used within this project
"""
from enum import Enum


class RobotType(Enum):
    HUMAN = 0
    SPIDER = 1


class ObjDist(Enum):
    AVG = 0
    LOCATION = 1
    X = 10
    Y = 11
    SUM = 2
    COUNT = 3
    LAST_SEEN = 4
    IS_FOUND = 5
    LIST = 6


class DurTypes(Enum):
    MAIN_LOOP = 0
    MAIN_DUR = 1
    MAIN_SUP_LOOP = 2
    MAIN_SUP_DUR = 3


if __name__ == "__main__":
    pass

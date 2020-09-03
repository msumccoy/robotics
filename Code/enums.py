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


class DistanceType(Enum):
    MAIN = 0
    LEFT = 1
    RIGHT = 2


if __name__ == "__main__":
    pass

""" Kuwin Wyke
Midwestern State University

This module contains constants that define specific types
"""
from enum import Enum


class IMG_LOC_TYPE(Enum):
    # Image Location Types
    CAM = 0
    FILE = 1


class COORDS_P(Enum):
    POINT1 = 0
    POINT2 = 1


class COORDS_XY(Enum):
    X = 0
    Y = 1

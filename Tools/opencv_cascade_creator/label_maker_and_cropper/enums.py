""" Kuwin Wyke
Midwestern State University

This module contains constants that define specific types
"""
from enum import Enum


class IMG_LOC_TYPE(Enum):
    # Image Location Types
    CAM = 0
    FILE = 1


class COORDS(Enum):
    POINT1 = 0
    POINT2 = 1
    X = 0
    Y = 1

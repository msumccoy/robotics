import sys
import pygame
import random

from sim_master import SimMaster


def main():
    print(
        "Take note that this game is primarily designed for one robot and "
        "one ball.\n"
        "While the game does have the functionality to have multiple balls "
        "and multiple robots all functionality is not implemented\n"
        "Namely robot collision, and ball collision (for blocking balls "
        "kicked by other players)"
    )

    sim_masters = [SimMaster(0), SimMaster(1)]

    sim_masters[0].start()


if __name__ == '__main__':
    main()






import time
import multiprocessing
import pygame

from sim_master import SimMaster
from config import FrameStepReturn as fsr
from config import Conf
from variables import ExitCtr, DoFlag, Gen, Frames


def frame_step_tester():
    """
    This function is used to test sim_master.SimMaster.frame_step
    as well helps demonstrate how to utilize the method
    """

    def print_return(ret):
        x, y = ret[fsr.X],ret[fsr.Y]
        b_flag = ret[fsr.BALL_FLAG]
        b_theta = ret[fsr.BALL_THETA]
        b_dist = ret[fsr.BALL_DIST]
        o_g_theta = ret[fsr.OWN_GOAL_THETA]
        o_g_dist = ret[fsr.OWN_GOAL_DIST]
        g_theta = ret[fsr.OPP_GOAL_THETA]
        g_dist = ret[fsr.OPP_GOAL_DIST]

        is_kick = ret[fsr.IS_KICK_SUCCESS]
        is_accurate = ret[fsr.IS_KICK_ACCURATE]
        is_kicking = ret[fsr.IS_KICKING]
        is_moving = ret[fsr.IS_MOVING]
        is_b_move = ret[fsr.IS_BALL_MOVED]
        is_scored = ret[fsr.IS_GOAL_SCORED]
        t_ime = ret[fsr.TIME]
        action = (
            ret[fsr.ACT_DIR], ret[fsr.ACT_THETA], ret[fsr.ACT_DIST],
            ret[fsr.ACT_KICK], ret[fsr.ACT_CONT]
        )
        print(f"robot x: {x}, robot y: {y}")
        print(f"ball: flag-{b_flag}, theta-{b_theta}, dist-{b_dist}")
        print(f"o-goal: theta-{o_g_theta}, dist-{o_g_dist}")
        print(f"goal: theta-{g_theta}, dist-{g_dist}")
        print(
            f"kick: success-{is_kick}, accurate--{is_accurate},"
            f" kicking{is_kicking}"
        )
        print(f"moving: robot-{is_moving}, ball-{is_b_move}")
        print(f"scored {is_scored}, time {t_ime}")
        print(f"action : {action}")
        print(f"Current time {Frames.time()}\n")

    def neural_net_simulator(index):
        sim_master = SimMaster(index)
        direction = theta = dist = kick = cont = 0

        # Last time timeout was reset
        timeout1 = timeout2 = timeout3 = timeout4 = 0

        # Start the test loop and continue while generic exit control allows
        while ExitCtr.gen:
            # Run simulation step and get return state
            ret = sim_master.frame_step([direction, theta, dist, kick, cont])

            # Get keys currently being pressed
            keys = pygame.key.get_pressed()

            # Reset all variables
            theta = dist = kick = 0
            cont = 1
            f_print = False  # Flag for printing

            # Activate different testing functionality  ######################
            # Manual control)
            if keys[pygame.K_UP]:
                dist = Conf.MOVE_DIST * 30
            if keys[pygame.K_RIGHT]:
                direction = 1
                theta = Conf.DIR_OFFSET * 3
            if keys[pygame.K_LEFT]:
                direction = 0
                theta = Conf.DIR_OFFSET * 3

            # Activate print function
            if keys[pygame.K_p]:
                f_print = True

            # Send kick
            if keys[pygame.K_SPACE] and time.time() - timeout1 > Conf.CD_TIME:
                timeout1 = time.time()
                kick = 1

            # Actually send commands i.e. don't send continue
            if keys[pygame.K_s] and time.time() - timeout2 > Conf.CD_TIME:
                timeout2 = time.time()
                cont = 0
            ##################################################################
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    ExitCtr.gen = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        ExitCtr.gen = False
            if f_print:
                print_return(ret)
            time.sleep(.01)
        sim_master.exit()

    net_sims = []
    for i in range(Conf.NUM_PROC):
        net_sims.append(
            multiprocessing.Process(target=neural_net_simulator, args=(i,))
        )

    for proc in net_sims:
        proc.start()
    for proc in net_sims:
        proc.join()


if __name__ == "__main__":
    frame_step_tester()

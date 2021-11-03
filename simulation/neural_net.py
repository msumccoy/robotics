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

    def show_window(ret):
        import matplotlib.pyplot as plt

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

        msg = (
            f"robot x: {x}, robot y: {y}\n"
            f"ball: flag-->{b_flag}, theta-->{int(b_theta)},"
            f" dist-->{int(b_dist)}\n"
            f"o-goal: theta-->{int(o_g_theta):}, dist-->{int(o_g_dist)}\n"
            f"goal: theta-->{int(g_theta)}, dist-->{int(g_dist)}\n"
            f"kick: success-->{is_kick}, accurate-->{is_accurate}\n"
            f"kicking-->{is_kicking}\n"
            f"moving: robot-->{is_moving}, ball-->{is_b_move}\n"
            f"scored {is_scored}, time {int(t_ime)}\n"
            f"action : {action}\n"
            f"Current time {int(Frames.time())}\n"
            f"Time from start {int(Frames.time_from_start())}\n"
        )

        plt.ion()
        plt.cla()
        plt.text(0, 100, msg, clip_on=False, font={'size':15})
        plt.axis([0, 500, 0, 500])
        plt.axis('off')
        plt.pause(0.00000001)

        plt.show()

    def print_return(ret):
        if ret is None:
            return
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
        print(f"ball: flag-->{b_flag}, theta-->{b_theta}, dist-->{b_dist}")
        print(f"o-goal: theta-->{o_g_theta}, dist-->{o_g_dist}")
        print(f"goal: theta-->{g_theta}, dist-->{g_dist}")
        print(
            f"kick: success-->{is_kick}, accurate-->{is_accurate},"
            f" kicking-->{is_kicking}"
        )
        print(f"moving: robot-->{is_moving}, ball-->{is_b_move}")
        print(f"scored {is_scored}, time {t_ime}")
        print(f"action : {action}")
        print(f"Current time {Frames.time()}\n")

    def neural_net_simulator(index):
        sim_master = SimMaster(index)
        direction = theta = dist = kick = cont = 0
        num = 1

        # Last time timeout was reset
        timeout1 = timeout2 = timeout3 = timeout4 = 0

        # Stop flags
        print_flag = False
        s_kick = g_kick = a_kick = c_kick = t_move = b_move = False

        # Start the test loop and continue while generic exit control allows
        while ExitCtr.gen:
            # Run simulation step and get return state
            ret = sim_master.frame_step([direction, theta, dist, kick, cont])

            # Diplay conditions in pyplot window
            if DoFlag.show_plt:
                show_window(ret)
            # Get keys currently being pressed
            keys = pygame.key.get_pressed()
            mods = pygame.key.get_mods()

            # Reset all variables
            theta = dist = kick = 0
            cont = 1

            # Activate different testing functionality  ######################
            # Manual control)
            if keys[pygame.K_UP]:
                if num == 0:
                    sim_master.robot.move(Conf.UP)
                dist = num
            elif keys[pygame.K_DOWN]:
                if num == 0:
                    sim_master.robot.move(Conf.DOWN)
            if keys[pygame.K_RIGHT]:
                if num == 0:
                    sim_master.robot.move(Conf.RIGHT)
                direction = 1
                theta = num * 20
            elif keys[pygame.K_LEFT]:
                if num == 0:
                    sim_master.robot.move(Conf.LEFT)
                direction = 0
                theta = num * 20
            if num == 0:
                dist_temp = 5
                if keys[pygame.K_i] or keys[pygame.K_KP8]:
                    # Move up
                    sim_master.ball.move(-90, dist_temp)
                elif keys[pygame.K_k] or keys[pygame.K_KP5]:
                    # Move down
                    sim_master.ball.move(90, dist_temp)
                if keys[pygame.K_j] or keys[pygame.K_KP4]:
                    # Move left
                    sim_master.ball.move(180, dist_temp)
                elif keys[pygame.K_l] or keys[pygame.K_KP6]:
                    # Move right
                    sim_master.ball.move(0, dist_temp)

            # Toggle condition flags (for stopping or printing ect.
            # goal (own or otherwise)
            # Kick accuracy
            # Kick success (if a kick was done whether it connected and if
            #   not what the current conditions are
            # if moving
            # if kicking
            # if ball moved
            # If control is pressed: left (4160) Right (4224)
            if (
                    (mods == 4160 or mods == 4224)
                    and time.time() - timeout1 > Conf.CD_TIME
            ):
                if keys[pygame.K_k]:  # Toggle kick stop flag
                    timeout1 = time.time()
                    s_kick = not s_kick
                    if s_kick:
                        print("Stop on kick activated")
                    else:
                        print("Stop on kick disabled")
                if keys[pygame.K_g]:  # Toggle goal stop flag
                    timeout1 = time.time()
                    g_kick = not g_kick
                    if g_kick:
                        print("Stop on goal activated")
                    else:
                        print("Stop on goal disabled")
                if keys[pygame.K_a]:  # Toggle accuracy stop flag
                    timeout1 = time.time()
                    a_kick = not a_kick
                    if a_kick:
                        print("Stop on accuracy activated")
                    else:
                        print("Stop on accuracy disabled")
                if keys[pygame.K_c]:  # Toggle currently kicking print flag
                    timeout1 = time.time()
                    c_kick = not c_kick
                    if c_kick:
                        print("Currently kicking flag activated")
                    else:
                        print("Currently kicking flag disabled")
                if keys[pygame.K_t]:  # Toggle robot moving print flag
                    timeout1 = time.time()
                    t_move = not t_move
                    if t_move:
                        print("Print on move activated")
                    else:
                        print("Print on move disabled")
                if keys[pygame.K_b]:  # Toggle ball  moving print flag
                    timeout1 = time.time()
                    b_move = not b_move
                    if b_move:
                        print("Print on move activated")
                    else:
                        print("Print on move disabled")

            # Stop when specific events occur  ###############################
            if s_kick and ret[fsr.ACT_KICK] == 1 and ret[fsr.ACT_CONT] == 0:
                # If kick was attempted pause and print
                print("KICK ATTEMPTED")
                time.sleep(2)
            if g_kick and ret[fsr.IS_GOAL_SCORED] == 1:
                # If goal was scored pause and print
                print("Goal scored")
                time.sleep(2)
            elif a_kick and ret[fsr.IS_KICK_ACCURATE] == 1:
                # If ball hit close to goal pause and print
                print("Ball hit close to goal")
                time.sleep(2)
            if c_kick and ret[fsr.IS_KICKING] == 1:
                # If currently kicking print
                print("Currently kicking")
            if t_move and ret[fsr.IS_MOVING] == 1:
                # If robot is moving print
                print("Robot is moving")
            elif b_move and ret[fsr.IS_BALL_MOVED] == 1:
                # If ball is moving print
                print("The ball is currently moving")
            #################################################################

            # Activate print function and toggle show plt
            if keys[pygame.K_p] and time.time() - timeout1 > Conf.CD_TIME:
                timeout1 = time.time()
                print_flag = True
                DoFlag.show_plt = not DoFlag.show_plt

            # Send kick
            if keys[pygame.K_SPACE] and time.time() - timeout2 > Conf.CD_TIME:
                timeout2 = time.time()
                kick = 1
                cont = 0

            # Actually send commands i.e. don't send continue
            if keys[pygame.K_s] and time.time() - timeout3 > Conf.CD_TIME:
                timeout3 = time.time()
                cont = 0

            #  Manually reset game
            if keys[pygame.K_r] and time.time() - timeout4 > Conf.CD_TIME:
                timeout4 = time.time()
                sim_master.rest_positions()

            # Set move/angle adjustment value
            if keys[pygame.K_0]:
                num = 0
            elif keys[pygame.K_1]:
                num = 1
            elif keys[pygame.K_2]:
                num = 2
            elif keys[pygame.K_3]:
                num = 3
            elif keys[pygame.K_4]:
                num = 4
            elif keys[pygame.K_5]:
                num = 5
            elif keys[pygame.K_6]:
                num = 6
            elif keys[pygame.K_7]:
                num = 7
            elif keys[pygame.K_8]:
                num = 10
            elif keys[pygame.K_9]:
                num = 15
            elif keys[pygame.K_w]:
                num = 20

            ##################################################################
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    ExitCtr.gen = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        ExitCtr.gen = False
            if print_flag:
                print_flag = False
                print_return(ret)
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

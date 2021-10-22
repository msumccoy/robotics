import time


def frame_step_tester():
    """
    This function is used to test sim_master.SimMaster.frame_step
    as well helps demonstrate how to utilize the method
    """
    import multiprocessing
    from sim_master import SimMaster
    from config import FrameStepReturn as fsr
    from config import Conf

    def neural_net_simulator(index):
        sim_master = SimMaster(index)
        for i in range(300):
            if i == 0:
                a = 300
                b = 0
            else:
                a = 0
                b = 1
            ret = sim_master.frame_step([0,0,a,0,b])
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
                f"kick: success-{is_kick}, acurate{is_accurate},"
                f" kicking{is_kicking}"
            )
            print(f"moving: robot-{is_moving}, ball-{is_b_move}")
            print(f"scored {is_scored}, time {t_ime}")
            print(f"action : {action}")
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

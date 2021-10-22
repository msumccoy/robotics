

def frame_step_tester():
    """
    This function is used to test sim_master.SimMaster.frame_step
    as well helps demonstrate how to utilize the method
    """
    import multiprocessing
    from sim_master import SimMaster

    from config import Conf

    def neural_net_simulator():
        pass

    net_sims = []
    for i in range(Conf.NUM_PROC):
        net_sims.append(multiprocessing.Process(target=neural_net_simulator))

    for proc in net_sims:
        proc.start()
    for proc in net_sims:
        proc.join()


if __name__ == "__main__":
    frame_step_tester()

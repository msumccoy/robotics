import multiprocessing

from sim_master import SimMaster
from config import Conf, GS


def main():
    print(  # Out dated info?
        "Take note that this game is primarily designed for one robot and "
        "one ball.\n"
        "While the game does have the functionality to have multiple balls "
        "and multiple robots all functionality is not implemented\n"
        "Namely robot collision, and ball collision (for blocking balls "
        "kicked by other players)"
    )

    sim_masters = []  # store different simulation controllers
    sim_processes = []  # store the individual simulation processes

    # Create a simulation controller and process for the set number
    for i in range(Conf.NUM_PROC):
        sim_masters.append(SimMaster(i, algorithm=GS.TYPE_MAN))
        sim_masters[i].load()
        sim_processes.append(
            multiprocessing.Process(target=sim_masters[i].start_man_calc)
        )

    # Start the processes and wait for them to end
    for proc in sim_processes:
        proc.start()
    for proc in sim_processes:
        proc.join()


if __name__ == '__main__':
    main()

# For realistic simulation
# TODO: give a probabilistic location rather than precise
#  - Get robot to look for markers to determine location
#    > stop feeding position until markers found

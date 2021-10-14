import multiprocessing

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

    num_sim = 1
    sim_masters = []
    sim_processes = []
    for i in range(num_sim):
        sim_masters.append(SimMaster(i))
        sim_processes.append(
            multiprocessing.Process(target=sim_masters[i].start)
        )

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

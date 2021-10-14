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

    sim_masters = [SimMaster(0), SimMaster(1)]

    master0 = multiprocessing.Process(target=sim_masters[0].start)
    master1 = multiprocessing.Process(target=sim_masters[1].start)

    master0.start()
    master1.start()

    master0.join()
    master1.join()


if __name__ == '__main__':
    main()

# For realistic simulation
# TODO: give a probabilistic location rather than precise
#  - Get robot to look for markers to determine location
#    > stop feeding position until markers found

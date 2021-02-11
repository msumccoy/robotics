"""
This file is to be used to test several concepts such as creation of ram
disks, pipes, communication between separate processes, running tkinter in
separate process from the rest of the program. If multiprocessing still
produces error we will have to create two entirely different programs that
communicate via pipes the same way they would communicate in a multiprocessing
environment.
"""

# TODO: Verify existence of ramdisk
# TODO: create pipe
#  communicate via pipes
# TODO: create simple robot communication
# TODO: create simple camera interface
# TODO: create simple gui
# TODO: get all three separate processes to communicate via pipes


from config import Conf
from variables import Alert


def main():
    if Alert.ramdisk:
        # create and start processes
        print("Start all processes")
    else:
        print(
            "only start robot control (auto initially disabled)(cli control)"
        )


if __name__ == '__main__':
    main()

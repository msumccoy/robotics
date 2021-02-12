"""
This file is to be used to test several concepts such as creation of ram
disks, pipes, communication between separate processes, running tkinter in
separate process from the rest of the program. If multiprocessing still
produces error we will have to create two entirely different programs that
communicate via pipes the same way they would communicate in a multiprocessing
environment.
"""

# TODO: Verify existence of ramdisk
# TODO: create simple robot communication
# TODO: create simple camera interface
# TODO: create simple gui
# TODO: Camera and robot in same thread gui in secondary process
# TODO: get GUI processes to communicate via pipe


from config import Conf
from variables import Alert


def mock_robot():
    print("mock robot")
    with open(Conf.PIPE_GUI, "w") as pipe:
        # This needs to be done in a sub process as opening the pipe locks
        # the system up until read from
        print("writing to pipe")
        pipe.write("test")
        print("wrote to pipe")


def mock_camera():
    pass


def mock_gui():
    with open(Conf.PIPE_GUI, "r") as pipe:
        pipe.read(4)


def main():
    if Alert.ramdisk:
        # create and start processes
        print("Start gui process and remainder of program is in main process")
        mock_robot()
        mock_gui()
    else:
        print(
            "only start robot control (auto initially disabled)(cli control)"
        )


if __name__ == '__main__':
    main()

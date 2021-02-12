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


import subprocess
import threading
import time

from config import Conf
from variables import Active


def pipe_handle():
    with open(Conf.PIPE_GUI, "w", 0) as pipe:
        # This needs to be done in a sub process as opening the pipe locks
        # the system up until read from
        print("writing to pipe")
        pipe.write("test test")
        print("test test")
        time.sleep(1)
        pipe.write("test1 test1")
        print("test test2")
        time.sleep(1)
        pipe.write("test2 test2")
        print("test test2]1")
        time.sleep(1)
        print("wrote to pipe")


def mock_robot():
    # Named pipe test: writing side can lock with no problem as it will be
    # running it an independent thread
    print("mock robot")
    pipe_handle()


def mock_camera():
    pass


def mock_gui():
    # Named pipe test: Reading should not lock if writing side is not
    # currently writing because this will result in GUI locking up
    #
    # On that note there needs to be at least two pipes:
    #       one for the video, one for the text info
    print("reading pipe")
    with open(Conf.PIPE_GUI, "r", 0) as pipe:
        print(pipe.read(50))
    print("reading complete")


def main():
    if Active.ramdisk:
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

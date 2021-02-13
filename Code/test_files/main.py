"""
Currently the objctive is to test passing video stream over sockets
"""

# TODO: test connecting two separate processes via sockets

import multiprocessing
import time

from config import Conf


def mock_robot():
    pass


def mock_camera():
    pass


def mock_gui():
    pass


def process1():
    # Socket server
    num = 100
    for i in range(num):
        print(f"process1 at {i} out of {num}")
        time.sleep(.1)


def process2():
    # Socket client
    num = 100
    for i in range(num):
        print(f"process2 at {i} out of {num}")
        time.sleep(.5)


def main():
    # Deamon processes will die after main program ends
    proc1 = multiprocessing.Process(target=process1, daemon=True)
    proc2 = multiprocessing.Process(target=process2, daemon=True)

    proc1.start()
    proc2.start()

    time.sleep(5)

    print(f"status of proc1:name={proc1.name}, alive={proc1.is_alive()}")
    print(f"status of proc2:name={proc2.name}, alive={proc2.is_alive()}")

    proc1.join(100)


if __name__ == '__main__':
    main()

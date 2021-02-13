"""
Currently the objctive is to test passing video stream over sockets
"""

# TODO: test connecting two separate processes via sockets

import multiprocessing
import select
import socket
import time

from config import Conf
from socket_functions import read_transmission


def mock_robot():
    pass


def mock_camera():
    pass


def mock_gui():
    pass


def process1():
    # Socket server
    sever_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sever_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sever_socket.bind((Conf.LOCAL_IP, Conf.PING_MONITOR_PORT))
    sever_socket.listen()
    socket_list = [sever_socket]
    while True:
        time.sleep(1)

        read_sockets, _, exception_sockets = select.select(
            socket_list, [], socket_list, 0
        )
        for notified_socket in read_sockets:
            if notified_socket is sever_socket:
                client_socket, client_address = sever_socket.accept()
                socket_list.append(client_socket)
                notified_socket = client_socket

            com_response = read_transmission(notified_socket)
            if com_response is False:
                socket_list.remove(notified_socket)
            else:
                for i in range(com_response[0]):
                    data_type, data = com_response[i+1]
                    print(f"data_type {data_type}: data {data}")
                    if data_type == Conf.COM_TEST:
                        print("Test type")  # debug  ################
                        if data == ComDataType.HOME_INFO.value:
                            # State number of segments being sent
                            com_data = ComFunc.make_fixed_string(
                                Conf.PRE_HEADER_LEN, 2
                            )
                            com_data += Com.get_stats()
                            com_data += Com.get_ping_status()

                            try:
                                notified_socket.send(com_data)
                            except Exception as e:
                                print(e)
                                print(type(e))
                                print("sending error in main loop")
                        else:
                            raise TypeError(
                                "Comunication server: Unknown data type "
                                "received in main loop request"
                            )
                    else:
                        raise TypeError(
                            "Unknown data type received in main loop: "
                            "data_type = {}".format(data_type)
                        )


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

    proc1.join(100)


if __name__ == '__main__':
    main()

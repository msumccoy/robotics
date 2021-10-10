"""
Currently the objective is to test passing video stream over sockets

socket communication
sent list must have the form
[num_items, [data_type0, data0], [data_type1, data1], ..., [data_typeN-1, dataN-1], [data_typeN, dataN]]
"""

# TODO: test connecting two separate processes via sockets (completed)

import multiprocessing
import select
import socket
import time
import cv2
import numpy as np
import base64

from config import Conf
from socket_functions import read_transmission, make_fixed_string, code_list, decode_list


def mock_robot():
    pass


def mock_camera():
    pass


def mock_gui():
    pass


def socket_server():
    # Socket server
    sever_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sever_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sever_socket.bind((Conf.LOCAL_IP, Conf.PING_MONITOR_PORT))
    sever_socket.listen()
    socket_list = [sever_socket]
    cam = cv2.VideoCapture(2)
    while True:
        _, frame = cam.read()
        cv2.imshow("frame", frame)

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
                for i in range(com_response[Conf.NUM_SEGMENTS]):
                    data_type, data = com_response[i+1]
                    print(f"socket_server: data_type {data_type}: data {data}")
                    if data_type == Conf.COM_TEST:
                        print("Test type")  # debug  ################
                        com_data = make_fixed_string(
                                Conf.PRE_HEADER_LEN, 1
                            )
                        encoded, buffer = cv2.imencode('.jpg', frame)
                        jpg_as_text = base64.b64encode(buffer)
                        com_data += code_list([jpg_as_text], Conf.COM_TEST2)
                        print(f"Server side printing: {data}")
                        notified_socket.send(com_data)
                    else:
                        raise TypeError(
                            "Unknown data type received in main loop: "
                            "data_type = {}".format(data_type)
                        )
        k = cv2.waitKey(1)
        if k == ord('a'):
            print(jpg_as_text)
        elif k != -1 and k != 255:
            break


def socket_client():
    # Socket client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((Conf.LOCAL_IP, Conf.PING_MONITOR_PORT))
    client_socket.setblocking(False)
    for i in range(10):
        com_data = make_fixed_string(Conf.PRE_HEADER_LEN, 1)
        com_data += code_list([f"testing {i}"], Conf.COM_TEST)
        client_socket.send(com_data)
        com_response = read_transmission(client_socket)
        print(f"socket_client: num segments: {com_response[0]}")
        for j in range(com_response[Conf.NUM_SEGMENTS]):
            data_type, data = com_response[j+1]
            print(f"socket_client: data_type --> {data_type}, data --> {data}")
        time.sleep(1)
        print("socket_client: round again we go")


def main():
    # Daemon processes will die after main program ends
    proc1 = multiprocessing.Process(target=socket_server, daemon=True)
    proc2 = multiprocessing.Process(target=socket_client, daemon=True)

    proc1.start()
    time.sleep(2)
    proc2.start()

    proc1.join()


if __name__ == '__main__':
    main()

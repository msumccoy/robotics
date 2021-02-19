import logging
import select
import socket
import time

import log_set_up  # This must Always be the first custom module imported
from camera import Camera
from config import Conf
from misc import pretty_time
from robot_control import Robot
from socket_functions import read_transmission, make_fixed_string, code_list
from variables import ExitControl


class SocketServer:
    main_logger = logging.getLogger(Conf.LOG_MAIN_NAME)
    logger = logging.getLogger(Conf.LOG_SOCKET_NAME)

    def __init__(self, robot_type):
        self.main_logger.info(f"Camera: started on version {Conf.VERSION}")
        self.logger.info(
            f"Started on version {Conf.VERSION}\n"
            f"- robot_type: {robot_type}"
        )
        self.start_time = time.time()
        self.sever_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sever_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sever_socket.bind((Conf.LOCAL_IP, Conf.PING_MONITOR_PORT))
        self.sever_socket.listen()
        self.socket_list = [self.sever_socket]
        self.cam = Camera.get_inst(robot_type)
        self.robot = Robot.get_inst(robot_type)
        self.logger.info(f"Socket init ran in {pretty_time(self.start_time)}")

    def start(self):
        self.logger.info("Socket server started")
        while ExitControl.gen and ExitControl.socket:
            time.sleep(1)

            read_sockets, _, exception_sockets = select.select(
                self.socket_list, [], self.socket_list, 0
            )
            for notified_socket in read_sockets:
                if notified_socket is self.sever_socket:
                    client_socket, client_address = self.sever_socket.accept()
                    self.socket_list.append(client_socket)
                    notified_socket = client_socket

                com_response = read_transmission(notified_socket)
                if com_response is False:
                    self.socket_list.remove(notified_socket)
                else:
                    for i in range(com_response[Conf.NUM_SEGMENTS]):
                        data_type, data = com_response[i+1]
                        print(
                            f"socket_server: "
                            f"data_type {data_type}: data {data}"
                        )
                        if data_type == Conf.TEST:
                            print("Test type")  # debug  ################
                            com_data = make_fixed_string(
                                    Conf.PRE_HEADER_LEN, 1
                                )
                            com_data += code_list(["testing"], Conf.TEST)
                            print(f"Server side printing: {data}")
                            notified_socket.send(com_data)
                        else:
                            raise TypeError(
                                "Unknown data type received in main loop: "
                                "data_type = {}".format(data_type)
                            )

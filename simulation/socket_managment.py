import errno
import pickle
import select
import socket
import time

from variables import ExitCtr
from config import Sock, ComDataType


class Com:
    @staticmethod
    def ping_com_control():
        sever_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sever_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sever_socket.bind((Sock.IP, Sock.PORT))
        sever_socket.listen()
        socket_list = [sever_socket]
        while ExitCtr.gen:
            time.sleep(1)
            read_sockets, _, exception_sockets = select.select(
                socket_list, [], socket_list, 0)
            for notified_socket in read_sockets:
                if notified_socket is sever_socket:
                    client_socket, client_address = sever_socket.accept()
                    socket_list.append(client_socket)
                    notified_socket = client_socket

                com_response = ComFunc.read_transmission(notified_socket)
                if com_response is False:
                    socket_list.remove(notified_socket)
                else:
                    for i in range(com_response[0]):
                        data_type, data = com_response[i+1]
                        if data_type == ComDataType.TEXT:
                            print(f"{data_type}: {data}")


class ComFunc:
    """
    This class is used to group communication functions for both the ping
    monitor and web server.
    """
    @classmethod
    def connect(cls, current_socket):
        """
        :param current_socket: soccet to be used
        :return: True for success false for failure

        This function is used by the web server to connect to the ping monitor
        """
        try:
            current_socket.connect((Sock.IP, Sock.PORT))
            time.sleep(2)
            current_socket.setblocking(False)
            request = cls.create_request()
            current_socket.send(request)
            return True
        except ConnectionError as e:
            print(e)
            return False
        except Exception as e:
            print(e)
            print(type(e))
            print("Unexpected error in connection attempt")
            return False

    @classmethod
    def create_request(cls, request_type=None, data_list=None):
        """
        :param request_type: list of request types
        :param data_list: data to be put into request
        :return: Formatted request to be sent via sockets
        """
        if data_list is None and request_type is None:
            data_list = [ComDataType.TEXT]
            request_type = [ComDataType.TEXT]

        if type(data_list) is not list or type(request_type) is not list:
            raise TypeError(
                "create_request  wrong data type:  ",
                type(data_list), type(request_type)
            )
        if len(data_list) != len(request_type):
            raise AttributeError(
                F"data length {len(data_list)} != request type length "
                F"{len(request_type)}"
            )

        # Information to tell receiving end how many things there are to
        # receive
        num_segments = cls.make_fixed_string(
            Sock.PRE_HEADER_LEN, len(data_list)
        )
        request = num_segments
        for rt, data in zip(request_type, data_list):
            if rt == ComDataType.TEXT:
                data_type = cls.make_fixed_string(
                    Sock.PRE_HEADER_LEN, ComDataType.TEXT
                )

                data = bytes(str(data), Sock.ENCODING)

                header = cls.make_fixed_string(Sock.HEADER_LEN, len(data))
                request += data_type + header + data
            else:
                raise TypeError("Unknown request type")
        return request

    @staticmethod
    def make_fixed_string(section_len, info):
        """
        :param section_len: Number of characters allocated to information
        :param info: desired information to transmit
        :return: formatted string as type byte
        """
        string = ("{:<" + str(section_len) + "}").format(info)
        string = bytes(string, Sock.ENCODING)
        return string

    @classmethod
    def read_transmission(cls, current_socket):
        """
        :param current_socket: network socket to use
        :return: list with number of segments then each segment type and data

        This function is used to read transmission between sockets.
        It used by both the ping monitor and web server
        """
        response = []
        while True:
            try:
                # Get the number of segments in the package
                num_segments = current_socket.recv(Sock.PRE_HEADER_LEN)
                if not len(num_segments):
                    return False
                num_segments = int(num_segments.decode(Sock.ENCODING).strip())
                response.append(num_segments)
                for _ in range(num_segments):
                    data_type = current_socket.recv(Sock.PRE_HEADER_LEN)
                    data_type = int(data_type.decode(Sock.ENCODING).strip())
                    segment = [data_type, cls.decode_pickle(current_socket)]
                    response.append(segment)
                return response
            except IOError as e:
                if (e.errno != errno.EAGAIN and
                        e.errno != errno.EWOULDBLOCK):
                    print(f'Reading error: {e}')
                    return False
            except Exception as e:
                print("unexpected error:   {e}")
                return False

    @staticmethod
    def decode_pickle(current_socket):
        """
        This function is not used* but it is used to decode python's built in
        pickle function and is used in tandem with cls.code_pickle
        """
        pickle_header = current_socket.recv(Sock.HEADER_LEN)
        pickle_len = int(pickle_header.decode(Sock.ENCODING).strip())
        return pickle.loads(current_socket.recv(pickle_len))

    @staticmethod
    def code_pickle(data_type, data):
        """
        This function is not used* but it is used to code python's built in
        pickle function and is used in tandem with cls.decode_pickle
        """
        data_type = (
            ("{:<" + str(Sock.PRE_HEADER_LEN) + "}").format(data_type)
        )
        data_type = bytes(data_type, Sock.ENCODING)
        data = pickle.dumps(data)
        header = (
            ("{:<" + str(Sock.HEADER_LEN) + "}").format(len(data))
        )
        header = bytes(header, Sock.ENCODING)
        return data_type + header + data



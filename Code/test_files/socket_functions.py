import ast
import errno

from config import Conf


def read_transmission(current_socket):
    """
    :param current_socket: network socket to use
    :return: list with number of segments then each segment type and data
            [num segments, [data_type0, data0], [data_type1, data1],...]

    This function is used to read transmission between sockets.
    It used by both the ping monitor and web server
    """
    response = []
    while True:
        try:
            # Get the number of segments in the package
            num_segments = current_socket.recv(Conf.PRE_HEADER_LEN)
            if not len(num_segments):
                return False
            num_segments = int(num_segments.decode(Conf.ENCODING).strip())
            response.append(num_segments)
            for _ in range(num_segments):
                data_type = current_socket.recv(Conf.PRE_HEADER_LEN)
                data_type = int(data_type.decode(Conf.ENCODING).strip())
                segment = [data_type, decode_list(current_socket)]
                response.append(segment)
            return response
        except IOError as e:
            if (e.errno != errno.EAGAIN and
                    e.errno != errno.EWOULDBLOCK):
                print(f'read_transmission: Reading error --> {str(e)}')
                return False
        except Exception as e:
            print(f"read_transmission: unexpected error -->   {e}")
            return False


def decode_list(current_socket):
    list_header = current_socket.recv(Conf.HEADER_LEN)
    list_len = int(list_header.decode(Conf.ENCODING).strip())
    current_list = current_socket.recv(list_len)
    current_list = current_list.decode(Conf.ENCODING).strip()
    current_list = ast.literal_eval(current_list)
    return current_list


def code_list(current_list, data_type):
    """
    :param current_list: list of information to be sent
    :param data_type: type of information in the list
    :return: formatted data for sending

    This function is used to prepare information to be sent via socket
    """
    data_type = make_fixed_string(
        Conf.PRE_HEADER_LEN, data_type)
    current_list = str(current_list)
    current_list = bytes(current_list, Conf.ENCODING)
    header = make_fixed_string(
        Conf.HEADER_LEN, len(current_list))
    return data_type + header + current_list


def make_fixed_string(section_len, info):
    """
    :param section_len: Number of characters allocated to information
    :param info: desired information to transmit
    :return: formatted string as type byte
    """
    string = ("{:<" + str(section_len) + "}").format(info)
    string = bytes(string, Conf.ENCODING)
    return string
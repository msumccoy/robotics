import os
from config import Conf


def create_pos_n_neg():
    for file_type in [Conf.neg_folder]:

        for img in os.listdir(file_type):

            if file_type == Conf.pos_folder:
                line = (
                    file_type + img + ' 1 0 0 ' + Conf.pos_size + ' '
                    + Conf.pos_size + '\n')
                with open('info.dat', 'a') as f:
                    f.write(line)
            elif file_type == Conf.neg_folder:
                line = file_type + img + '\n'
                with open('bg.txt', 'a') as f:
                    f.write(line)

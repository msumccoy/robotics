"""
Kuwin Wyke
Midwestern State University

This program is used to randomize the order of the negative images
for successive uses of OpenCV's createsamples
"""
import os
import time
import random

from config import Conf



def main():
    random.seed(time.time())
    name_list = [
        name for name in os.listdir(Conf.TARGET_FOLDER)
        if os.path.isfile(Conf.TARGET_FOLDER + "/" + name)
        and name != Conf.NEG
    ]
    random_name_list = [
        "{}/{}_{}".format(
            Conf.TARGET_FOLDER, int(random.random() * 1000), name
        )
        for name in name_list
    ]
    random_name_list.sort()
    i = 0
    for name in name_list:
        full_name = Conf.TARGET_FOLDER + "/" + name
        name_change = random_name_list[i]
        os.rename(full_name, name_change)
        i += 1

    name_list = [
        Conf.TARGET_FOLDER + "/" + name
        for name in os.listdir(Conf.TARGET_FOLDER)
        if os.path.isfile(Conf.TARGET_FOLDER + "/" + name)
        and name != Conf.NEG
    ]
    with open(Conf.NEG, "w") as file:
        i = 0
        for name in name_list:
            name_change = str(i) + ".jpg"
            os.rename(name, Conf.TARGET_FOLDER + "/" + name_change)
            file.write(Conf.TARGET_FOLDER + "/" + name_change + "\n")
            i += 1


if __name__ == '__main__':
    main()
